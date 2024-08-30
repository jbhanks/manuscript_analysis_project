import os
import json
import re
import random
import time
import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from models import *
import logging

def group_by_key(list_of_dicts):
    grouped_info = {}
    for d in list_of_dicts:
        for key in d:
            grouped_info.setdefault(key, list()).append(d[key])
    return grouped_info

def split_info(info):
    infos = []
    for section in info:
        d = {}
        d[section['key']['contenu']] = section['value']['contenu']
        infos.append(d)
    return infos

def get_scripts(soup):
    scripts = soup.find_all('script', {'type' : 'text/javascript'})
    return scripts

def get_page_total(soup):
    tot_pages = int(soup.find("div", {"id": "paginate"}).find('input', {"id": "pagination-input"})['aria-label'].split('/')[1])
    return tot_pages


def check_request_status(request, url):
    try:
        if request is None or not hasattr(request, 'status_code'):
            return PageRequest(status="failed", result="Not a valid request object", url=url)

        if request.status_code in {403, 404}:
            return PageRequest(status="failed", result=request.status_code, url=url)

        if '<title>Access Denied</title>' in request.text:
            logging.info(f"Access was denied for {url}")
            return PageRequest(status="failed", result="access denied", url=url)

        if '<noscript>' in request.text:
            logging.info(f"JS is required for {url}")
            return PageRequest(status="failed", result="JavaScript is required", url=url)

        if request.status_code != 200:
            return PageRequest(status="failed", result=request.status_code, url=url)

        logging.info(f"Success for {url}")
        return PageRequest(status="success", result=request.text, url=url)

    except Exception as e:
        logging.info(f"Getting URL failure with exception for {url}: {str(e)}")
        return PageRequest(status="failed", result=str(e), url=url)



def basic_request(session, url):
    session.mount(url, HTTPAdapter(max_retries=3))
    try:
        request = session.get(url, timeout=random.uniform(3, 8))
        return check_request_status(request, url)
    except requests.exceptions.ReadTimeout:
        logging.info(f"Timed out for {url}")
        return PageRequest(status="failed", result="timeout", url=url)
    except requests.exceptions.ConnectionError:
        logging.info(f"Connection error {url}")
        return PageRequest(status="failed", result="connection error", url=url)
    except urllib3.exceptions.ReadTimeoutError:
        logging.info(f"Timed out for {url}")
        return PageRequest(status="failed", result="timeout", url=url)
    except Exception as e:
        logging.info(f"Error for {url}")
        logging.info(str(e))
        return PageRequest(status="failed", result= str(e), url=url)


def ff_request(url):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return PageRequest(status="success", result=html, url=url)


def save_image(imginfo, download_dir="Downloads/"):
    with open(download_dir + re.sub(' ', '_', imginfo['object']), 'wb') as handle:
        response = requests.get(imginfo['imgurl'], stream=True)

        if not response.ok:
            logging.debug("Image download not ok for + " + imginfo['imgurl'])
            logging.debug(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

def get_page_info(filepath):
    f = open(filepath, "r").read()
    pages = f.split('\n\n')
    ordered_pages = []
    for page in pages:
        info = OnePage()
        head = page.split('\n')[0]
        info.transliteration = page.split('\n',1)[1]
        info.source = head.split(', ')[0]
        info.plate = re.split('(\d+)', head.split(', ')[1])
        info.verses = head.split(', ')[2]
        ordered_pages.append(info)
    ordered_pages = sorted(ordered_pages, key=lambda element: (int(element.plate[1]), element.plate[2]))
    [setattr(page, 'plate', page.plate[1] + page.plate[2]) for page in ordered_pages]
    return ordered_pages


def get_blocks_of_pages(pages_list):
    new_lists = []
    for idx,page in enumerate(pages_list):
        if idx == 0:
            prev_idx = idx
            prev_p = int(page.plate[1])
            page.plate = page.plate[1] + page.plate[2]
            new_lists.append([page])
            continue
        if int(page.plate[1]) - prev_p == 0:
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists[-1].append(page)
            continue
        if int(page.plate[1]) - prev_p > 1:
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists.append([page])
            continue
        if int(page.plate[1]) - prev_p == 1:
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists[-1].append(page)
    return new_lists

def match_translit_to_imgurl(folio, ordered_pages):
    for n in range(30, folio.total_pages + 1):
        url = folio.baseurl + 'f' + str(n)
        data = ff_request(url)
        nfo = parse_paris_lib(data.result)
        if nfo == None:
            continue
        if nfo['plate'] in pagelist:
            nfolist.append(nfo)
        else:
            continue
        matching_plate = list(filter(lambda p: p.plate == nfo['plate'], ordered_pages))
        if len(matching_plate) > 1:
            logging.warning("More than one match for plate ", nfo['plate'], "skipping..")
            continue
        if len(matching_plate) == 0 or matching_plate == None:
            logging.warning("Plate ", nfo['plate'], "not found in transliteration document, skipping..")
            continue
        # Updates the original OnePage object wtih the imgurl for the object
        matching_plate[0].imgurl = nfo['imgurl']
        return ordered_pages

def extract_clean_json(info_script):
    txt2 = re.sub(".*?({.*}).*", r"\1", info_script, flags=re.DOTALL)
    txt3 = re.sub("\\\\\\\\\\\\", '||||||||', txt2)
    txt4 = re.sub("\\\\", '', txt3)
    txt5 = re.sub("\|\|\|\|\|\|\|\|", '\\\\', txt4)
    js_obj = json.loads(txt5)
    extracted = js_obj['contenu'][0]['contenu']
    return extracted

def parse_paris_lib(html):
    soup = BeautifulSoup(html, features='html5lib')
    try:
        imgurl = soup.find("div", {"id": "visuDocument"}).find('img')['src']
    except TypeError:
        return None
    plate = re.sub('View.* ', '', soup.find("div", {"id": "visuDocument"}).find('img')['alt'])
    return {'imgurl' : imgurl, 'plate' : plate}

def extract_info_bnf(scriptlist):
    content_script = [
    trimmed
    for script in scriptlist
    if (script_str := getattr(script, 'string', None)) and isinstance(script_str, str)
    if (trimmed := re.sub(r"^\s+", "", script_str)).startswith('var menuFragment')
    ][0]
    subscripts = content_script.split('; var')
    info_script = [s for s in subscripts if s.startswith(' informationsModel = JSON.parse')][0]
    return info_script
