from utils import *
from models import *

# sesh = requests.Session()

search = "https://gallica.bnf.fr/services/engine/search/sru?operation=searchRetrieve&exactSearch=false&collapsing=true&version=1.2&query=(dc.type%20all%20%22manuscrit%22)%20and%20(gallicapublication_date%3C=%221800%22)%20and%20(indexationdate%3C=%222024/09/01%22)&suggest=10&keywords="

search2 = 'https://gallica.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=dc.title%20all%20%22manuscripts%22&maximumRecords=10'

search3 = 'https://gallica.bnf.fr/SRU?version=1.2&operation=searchRetrieve&query=(dc.type%20all%20%22manuscrit%22)%20and%20(gallicapublication_date%3C=%221800%22)%20and%20(indexationdate%3C=%222024/09/01%22)&suggest=10&keywords='


url = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f33.item"
url = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f209.item"

# Test a basic request
# data = basic_request(sesh, url)

# Test a Selenium request
data = ff_request(url)

imginfo = parse_paris_lib(data['result'], download_dir="Downloads")

save_image(imginfo)

translit = '/home/jam/SUPERTANK/Neural Net/Codex Amrensis 47/AMR47.txt'

imgbaseurl = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f"
start_num = 33
num_pages = 14
max_page = start_num + num_pages





translit = '/home/jam/SUPERTANK/Neural Net/Codex Amrensis 47/AMR47.txt'
ordered_pages = get_page_info(translit)
sections = get_blocks_of_pages(ordered_pages)

section = sections[0]
starturl = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f33.item"
for idx,page in enumerate(section):
    print(idx, page)

########################


import os

# project_path = '/home/jam/SUPERTANK/Neural Net/'
# folders = os.listdir(project_path)

basepath = '/home/jam/SUPERTANK/Neural Net/Codex Amrensis 47/'
files = os.listdir(basepath)
urlfiles =  [f for f in files if not f.startswith('AMR')]


folio = FullFolio(
    transliteration_file = [f for f in files if f.startswith('AMR')][0],
    urls = [open(basepath + urlfile, 'r').read() for urlfile in urlfiles],
    )

folio.baseurl = re.sub('(.*/).*', r'\1', folio.urls[0])

data = ff_request(folio.baseurl)

html = data.result

soup = BeautifulSoup(html, features='html5lib')

folio.total_pages = get_page_total(soup)

###

manuscript_info = get_manuscript_info(soup)

# Update folio object with manuscript data
populate_empty_attributes(folio, manuscript_info)

plates = get_plate_info(folio, basepath)

save_images(plates[11:21])

folio.plates = plates


# ####


