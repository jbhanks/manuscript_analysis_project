import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import random
import time
import re
from models import *



def check_request_status(request, url):
    try:
        if request is None or not hasattr(request, 'status_code'):
            return {"status": "failed", "result": "Not a valid request object", "url": url}

        if request.status_code in {403, 404}:
            return {"status": "failed", "result": request.status_code, "url": url}

        if '<title>Access Denied</title>' in request.text:
            print(f"Access was denied for {url}")
            return {"status": "failed", "result": "access denied", "url": url}

        if '<noscript>' in request.text:
            print(f"JS is required for {url}")
            return {"status": "failed", "result": "JavaScript is required", "url": url}

        if request.status_code != 200:
            return {"status": "failed", "result": request.status_code, "url": url}

        print(f"Success for {url}")
        return {"status": "success", "result": request.text, "url": url}

    except Exception as e:
        print(f"Getting URL failure with exception for {url}: {str(e)}")
        return {"status": "failed", "result": str(e), "url": url}


def basic_request(session, url):
    session.mount(url, HTTPAdapter(max_retries=3))
    try:
        request = session.get(url, timeout=random.uniform(3, 8))

        return check_request_status(request, url)

    except requests.exceptions.ReadTimeout:
        return {"status": "failed", "result": "timeout", "url": url}
    except requests.exceptions.ConnectionError:
        return {"status": "failed", "result": "connection error", "url": url}
    except urllib3.exceptions.ReadTimeoutError:
        return {"status": "failed", "result": "timeout", "url": url}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "failed", "result": f"http failed too: {str(e)}", "url": url}


def ff_request(url):
    firefox_options = Options()
    firefox_options.add_argument("--headless")
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    html = driver.page_source
    driver.quit()
    return {"status" : "success", "result" : html}



def parse_paris_lib(html):
    soup = BeautifulSoup(html, features='html5lib')
    imgurl = soup.find("div", {"id": "visuDocument"}).find('img')['src']
    obj = soup.find("div", {"id": "visuDocument"}).find('img')['alt']
    return {'imgurl' : imgurl, 'object' : obj}

def save_image(imginfo, download_dir="Downloads/"):
    with open(download_dir + re.sub(' ', '_', imginfo['object']), 'wb') as handle:
        response = requests.get(imginfo['imgurl'], stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

def get_page_info(filepath):
    f = open(filepath, "r").read()
    pages = f.split('\n\n')
    orderpages = []
    for page in pages:
        info = OnePage()
        head = page.split('\n')[0]
        info.transliteration = page.split('\n',1)[1]
        info.source = head.split(', ')[0]
        info.plate = re.split('(\d+)', head.split(', ')[1])
        info.verses = head.split(', ')[2]
        orderpages.append(info)
    orderpages = sorted(orderpages, key=lambda element: (int(element.plate[1]), element.plate[2]))
    return orderpages


def get_blocks_of_pages(pages_list):
    new_lists = []
    for idx,page in enumerate(pages_list):
        if idx == 0:
            print(idx)
            print("first one!")
            prev_idx = idx
            prev_p = int(page.plate[1])
            page.plate = page.plate[1] + page.plate[2]
            new_lists.append([page])
            continue
        if int(page.plate[1]) - prev_p == 0:
            print(idx, prev_idx)
            print("opposite page!")
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists[-1].append(page)
            continue
        if int(page.plate[1]) - prev_p > 1:
            print(idx, prev_idx)
            print("A gap!")
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists.append([page])
            continue
        if int(page.plate[1]) - prev_p == 1:
            print(idx, prev_idx)
            print("consecutive!")
            prev_p = int(page.plate[1])
            prev_idx = idx
            page.plate = page.plate[1] + page.plate[2]
            new_lists[-1].append(page)
    return new_lists
