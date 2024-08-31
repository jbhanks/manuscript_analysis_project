import os
import json
import re
import random
import time
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import ReadTimeoutError
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from bs4 import BeautifulSoup
from models import OnePage, PageRequest

# Function to group dictionaries by their keys
def group_by_key(list_of_dicts):
    grouped_info = {}
    for d in list_of_dicts:
        for key, value in d.items():
            grouped_info.setdefault(key, []).append(value)
    return grouped_info

# Function to split the 'info' based on sections
def split_info(info):
    return [{section['key']['contenu']: section['value']['contenu']} for section in info]

# Function to extract all JavaScript scripts from the soup object
def get_scripts(soup):
    return soup.find_all('script', type='text/javascript')

# Function to extract the total number of pages from the soup object
def get_page_total(soup):
    pagination_input = soup.find("div", {"id": "paginate"}).find('input', {"id": "pagination-input"})
    return int(pagination_input['aria-label'].split('/')[1])

# Function to check the status of an HTTP request and handle errors
def check_request_status(request, url):
    if request is None or not hasattr(request, 'status_code'):
        return PageRequest(status="failed", result="Not a valid request object", url=url)

    if request.status_code in {403, 404}:
        return PageRequest(status="failed", result=request.status_code, url=url)

    if '<title>Access Denied</title>' in request.text:
        logging.info(f"Access was denied for {url}")
        return PageRequest(status="failed", result="access denied", url=url)

    if '<noscript>' in request.text:
        logging.info(f"JavaScript is required for {url}")
        return PageRequest(status="failed", result="JavaScript is required", url=url)

    if request.status_code != 200:
        return PageRequest(status="failed", result=request.status_code, url=url)

    logging.info(f"Success for {url}")
    return PageRequest(status="success", result=request.text, url=url)

# Function to perform a basic HTTP GET request with retry logic
def basic_request(session, url):
    session.mount(url, HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
    try:
        request = session.get(url, timeout=random.uniform(3, 8))
        return check_request_status(request, url)
    except (requests.exceptions.ReadTimeout, ReadTimeoutError):
        logging.info(f"Timed out for {url}")
        return PageRequest(status="failed", result="timeout", url=url)
    except requests.exceptions.ConnectionError:
        logging.info(f"Connection error for {url}")
        return PageRequest(status="failed", result="connection error", url=url)
    except Exception as e:
        logging.exception(f"Error occurred for {url}")
        return PageRequest(status="failed", result=str(e), url=url)

# Function to perform a Firefox WebDriver request in headless mode
def ff_request(url):
    options = Options()
    options.add_argument("--headless")
    # Ideally I would like to block loading of images at this step, but when I tried using `set_preference('permissions.default.image', 2)` it also changed the content rendering such that selectors were not available.
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()
    return PageRequest(status="success", result=html, url=url)

# Function to save an image from a URL
def save_image(page, download_dir="Downloads/"):
    filepath = os.path.join(download_dir, page.plate)
    page.imgpath = filepath
    response = requests.get(page.imgurl, stream=True)

    if not response.ok:
        logging.debug(f"Image download failed for {imginfo['imgurl']}: {response}")
        return

    with open(filepath, 'wb') as handle:
        for block in response.iter_content(1024):
            if block:
                handle.write(block)

# Function to extract and process page information from a file
def get_page_info(filepath):
    with open(filepath, "r") as f:
        pages = f.read().strip().split('\n\n')

    ordered_pages = []
    for page in pages:
        info = OnePage()
        head, transliteration = page.split('\n', 1)
        info.transliteration = transliteration
        info.doc_id, plate, info.verses = head.split(', ')
        info.plate = re.split(r'(\d+)', plate)
        ordered_pages.append(info)

    ordered_pages.sort(key=lambda p: (int(p.plate[1]), p.plate[2]))
    for page in ordered_pages:
        page.plate = page.plate[1] + page.plate[2]

    return ordered_pages

# Function to group pages into blocks based on consecutive plate numbers
def get_blocks_of_pages(pages_list):
    new_lists = []
    prev_plate = None
    for idx, page in enumerate(pages_list):
        plate_number = int(page.plate[1])
        if idx == 0 or plate_number - prev_plate == 1:
            if idx != 0:
                new_lists[-1].append(page)
            else:
                new_lists.append([page])
        else:
            new_lists.append([page])
        prev_plate = plate_number
    return new_lists

# Function to match transliteration data to image URLs
def match_translit_to_imgurl(start, end, baseurl, ordered_pages, pagelist):
    matching_plates = []
    for n in range(start, end + 1):
        time.sleep(round(random.uniform(2,5),3))
        url = f'{baseurl}f{n}'
        try:
            data = ff_request(url)
        except ConnectionResetError:
            logging.warning(f"Connection reset error for {url}")
            time.sleep(round(random.uniform(30,60),2))
            continue
        try:
            imgurl, plate = parse_plate_page(data.result)
        except TypeError:
            logging.warning(f"Skipping plate for {url}")
            continue

        if plate not in pagelist:
            continue

        matching_plate = [p for p in ordered_pages if p.plate == plate][0]
        matching_plate.url = url
        matching_plate.imgurl = imgurl
        matching_plates.append(matching_plate)
    return matching_plates

# Function to extract clean JSON data from a script tag
def extract_clean_json(info_script):
    txt = re.sub(r".*?({.*}).*", r"\1", info_script, flags=re.DOTALL)
    txt = re.sub(r"\\\\\\\\", '||||||||', txt)
    txt = re.sub(r"\\", '', txt)
    txt = re.sub(r"\|\|\|\|\|\|\|\|", '\\\\', txt)
    js_obj = json.loads(txt)
    return js_obj['contenu'][0]['contenu']

# Function to parse HTML and extract image URL and plate information
def parse_plate_page(html):
    soup = BeautifulSoup(html, 'html5lib')
    img = soup.find("div", {"id": "visuDocument"}).find('img')

    if img is None:
        return None

    imgurl = img['src']
    plate = re.sub(r'View.* ', '', img['alt'])
    # return folio
    return imgurl, plate

# Function to extract specific information from a list of scripts
def extract_info_bnf(scriptlist):
    content_script = next(
        re.sub(r"^\s+", "", getattr(script, 'string', ''))
        for script in scriptlist
        if isinstance((script_str := getattr(script, 'string', None)), str)
        if re.sub(r"^\s+", "", script_str).startswith('var menuFragment')
    )
    subscripts = content_script.split('; var')
    info_script = next(s for s in subscripts if s.startswith(' informationsModel = JSON.parse'))
    return info_script


def populate_empty_attributes(instance, data_dict):
    for key, value in data_dict.items():
        if hasattr(instance, key):
            current_value = getattr(instance, key)
            # Check if the attribute is None, an empty string, or an empty list
            if current_value is None or current_value == '' or (isinstance(current_value, list) and len(current_value) == 0):
                setattr(instance, key, value)


def get_manuscript_info(soup):
    scripts = get_scripts(soup)
    info_script = extract_info_bnf(scripts)
    extracted = extract_clean_json(info_script)
    infos = split_info(extracted)
    grouped_info = group_by_key(infos)
    grouped_info = {k.lower():v for k,v in grouped_info.items()}
    return grouped_info


def populate_empty_attributes(instance, data_dict):
    for key, value in data_dict.items():
        if hasattr(instance, key):
            current_value = getattr(instance, key)
            # Check if the attribute is None, an empty string, or an empty list
            if current_value is None or current_value == '' or (isinstance(current_value, list) and len(current_value) == 0):
                setattr(instance, key, value)


def get_plate_info(folio, basepath):
    translit = basepath + folio.transliteration_file
    ordered_pages = get_page_info(translit)
    pagelist = [page.plate for page in ordered_pages]
    matched = match_translit_to_imgurl(30, folio.total_pages, folio.baseurl, ordered_pages, pagelist)
    return matched


def save_images(pagelist):
    for page in pagelist:
        time.sleep(round(random.uniform(4,10),5))
        save_image(page)
