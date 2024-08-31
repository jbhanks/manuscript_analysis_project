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
    driver = webdriver.Firefox(options=options)
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()
    return PageRequest(status="success", result=html, url=url)

# Function to save an image from a URL
def save_image(imginfo, download_dir="Downloads/"):
    filepath = os.path.join(download_dir, re.sub(r'\s+', '_', imginfo['object']))
    response = requests.get(imginfo['imgurl'], stream=True)

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
        info.source, plate, info.verses = head.split(', ')
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
def match_translit_to_imgurl(folio, ordered_pages):
    for n in range(30, folio.total_pages + 1):
        url = f'{folio.baseurl}f{n}'
        data = ff_request(url)
        nfo = parse_paris_lib(data.result)

        if not nfo or nfo['plate'] not in pagelist:
            continue

        matching_plate = [p for p in ordered_pages if p.plate == nfo['plate']]

        if len(matching_plate) > 1:
            logging.warning(f"More than one match for plate {nfo['plate']}, skipping...")
            continue
        if not matching_plate:
            logging.warning(f"Plate {nfo['plate']} not found in transliteration document, skipping...")
            continue

        # Update the original OnePage object with the imgurl
        matching_plate[0].imgurl = nfo['imgurl']

    return ordered_pages

# Function to extract clean JSON data from a script tag
def extract_clean_json(info_script):
    txt = re.sub(r".*?({.*}).*", r"\1", info_script, flags=re.DOTALL)
    txt = re.sub(r"\\\\\\\\", '||||||||', txt)
    txt = re.sub(r"\\", '', txt)
    txt = re.sub(r"\|\|\|\|\|\|\|\|", '\\\\', txt)
    js_obj = json.loads(txt)
    return js_obj['contenu'][0]['contenu']

# Function to parse HTML and extract image URL and plate information
def parse_paris_lib(html):
    soup = BeautifulSoup(html, 'html5lib')
    img = soup.find("div", {"id": "visuDocument"}).find('img')

    if img is None:
        return None

    imgurl = img['src']
    plate = re.sub(r'View.* ', '', img['alt'])
    return {'imgurl': imgurl, 'plate': plate}

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
