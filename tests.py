from utils import *
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup


sesh = requests.Session()


url = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f33.item"

# Test a basic request
data = basic_request(sesh, url)

# Test a Selenium request
data = ff_request(url)







soup = BeautifulSoup(data['result'], features='html5lib')
imgurl = soup.find("div", {"id": "visuDocument"}).find('img')['src']
obj = soup.find("div", {"id": "visuDocument"}).find('img')['alt']


