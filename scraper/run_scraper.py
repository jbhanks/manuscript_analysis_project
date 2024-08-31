import os
import sys
from utils import *
from models import *

transliteration_dir = sys.argv[1]
download_path = sys.argv[2]

files = os.listdir(transliteration_dir)
urlfiles =  [f for f in files if not f.startswith('AMR')]

folio = FullFolio(
    transliteration_file = [f for f in files if f.startswith('AMR')][0],
    urls = [open(transliteration_dir + urlfile, 'r').read() for urlfile in urlfiles],
    )

folio.baseurl = re.sub('(.*/).*', r'\1', folio.urls[0])

data = ff_request(folio.baseurl)

html = data.result

soup = BeautifulSoup(html, features='html5lib')

folio.total_pages = get_page_total(soup)

manuscript_info = get_manuscript_info(soup)

# Update folio object with manuscript data
populate_empty_attributes(folio, manuscript_info)

plates = get_plate_info(folio, transliteration_dir)

save_images(plates)

folio.plates = plates

