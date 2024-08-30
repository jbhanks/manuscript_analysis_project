import os
from dotenv import load_dotenv
import urllib3

load_dotenv()

dirs = os.listdir(datapth)


for d in dirs:
    files = os.listdir(d)



def download_cambridge(url):
    request = session.get(url)
