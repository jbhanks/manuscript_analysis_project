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



# sections = get_blocks_of_pages(ordered_pages)

folio.baseurl = re.sub('(.*/).*', r'\1', folio.urls[0])

data = ff_request(folio.baseurl)

html = data.result

soup = BeautifulSoup(html, features='html5lib')

folio.total_pages = get_page_total(soup)


translit = basepath + folio.transliteration_file
ordered_pages = get_page_info(translit)

pagelist = [page.plate for page in ordered_pages]

# nfolist = []

# for n in range(30, folio.total_pages + 1):
#     url = folio.baseurl + 'f' + str(n)
#     data = ff_request(url)
#     nfo = parse_paris_lib(data.result)
#     if nfo == None:
#         continue
#     if nfo['plate'] in pagelist:
#         nfolist.append(nfo)
#     else:
#         continue
#     matching_plate = list(filter(lambda p: p.plate == nfo['plate'], ordered_pages))
#     if len(matching_plate) > 1:
#         print("More than one match for plate ", nfo['plate'], "skipping..")
#         continue
#     if len(matching_plate) == 0 or matching_plate == None:
#         print("Plate ", nfo['plate'], "not found in transliteration document, skipping..")
#         continue
#     # Updates the original OnePage object wtih the imgurl for the object
#     matching_plate[0].imgurl = nfo['imgurl']


# def match_translit_to_imgurl(folio, ordered_pages):
#     for n in range(30, folio.total_pages + 1):
#         url = folio.baseurl + 'f' + str(n)
#         data = ff_request(url)
#         nfo = parse_paris_lib(data.result)
#         if nfo == None:
#             continue
#         if nfo['plate'] in pagelist:
#             nfolist.append(nfo)
#         else:
#             continue
#         matching_plate = list(filter(lambda p: p.plate == nfo['plate'], ordered_pages))
#         if len(matching_plate) > 1:
#             print("More than one match for plate ", nfo['plate'], "skipping..")
#             continue
#         if len(matching_plate) == 0 or matching_plate == None:
#             print("Plate ", nfo['plate'], "not found in transliteration document, skipping..")
#             continue
#         # Updates the original OnePage object wtih the imgurl for the object
#         matching_plate[0].imgurl = nfo['imgurl']
#         return ordered_pages


# op2 = match_translit_to_imgurl(folio, ordered_pages)
###
scripts = get_scripts(soup)

info_script = extract_info_bnf(scripts)

extracted = extract_clean_json(info_script)

infos = split_info(extracted)

grouped_info = group_by_key(infos)


###


for page in ordered_pages:
    print(page.plate)

plate_url = "https://gallica.bnf.fr/ark:/12148/btv1b84152047/f33.item"
data = ff_request(plate_url)

html = data['result']
plate_info = parse_paris_lib(html)

#
# # def parse_paris_lib(html):

soup = BeautifulSoup(html, features='html5lib')
pag = soup.find("div", {"id": "paginate"})
view = pag.find('input', {"id": "pagination-input"})

tot_pages = int(soup.find("div", {"id": "paginate"}).find('input', {"id": "pagination-input"})['aria-label'].split('/')[1])

pag_num = re.sub('View ', '', view['aria-label']).split('/')

plate = re.sub('View.* ', '', soup.find("div", {"id": "visuDocument"}).find('img')['alt'])




# imgurl = soup.find("div", {"id": "visuDocument"}).find('img')['src']
# obj = soup.find("div", {"id": "visuDocument"}).find('img')['alt']


    # return {'imgurl' : imgurl, 'object' : obj}

########################

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


