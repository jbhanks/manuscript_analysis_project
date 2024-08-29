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



finished = []

for num in range(start_num, max_page + 1):
    url = imgbaseurl + str(num)
    data = ff_request(url)
    imginfo = parse_paris_lib(data['result'])
    save_image(imginfo)
    finished.append(imginfo)


