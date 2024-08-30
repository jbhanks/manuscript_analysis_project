from utils import *
from models import *

# sesh = requests.Session()


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
basepath = '/home/jam/SUPERTANK/Neural Net/Codex Amrensis 47/'
files = os.listdir(basepath)
urlfiles =  [f for f in files if not f.startswith('AMR')]

folio = FullFolio(
    transliteration_file = [f for f in files if f.startswith('AMR')][0],
    urls = [open(basepath + urlfile, 'r').read() for urlfile in urlfiles],
    )

folio.baseurl = re.sub('(.*/).*', r'\1', folio.urls[0])

data = ff_request(folio.baseurl)

html = data['result']

scripts = get_scripts(html)


info_script = extract_info_bnf(scripts)

extracted = extract_clean_json(info_script)

infos = split_info(extracted)

grouped_info = group_by_key(infos)


imgurl = soup.find("div", {"id": "visuDocument"}).find('img')['src']
obj = soup.find("div", {"id": "visuDocument"}).find('img')['alt']
    # return {'imgurl' : imgurl, 'object' : obj}

folio.pages.append(testpage)


#acc_1-0_panel_2
######################################
finished = []

for num in range(start_num, max_page + 1):
    url = imgbaseurl + str(num)
    data = ff_request(url)
    imginfo = parse_paris_lib(data['result'])
    save_image(imginfo)
    finished.append(imginfo)


