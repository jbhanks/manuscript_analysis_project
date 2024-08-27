import os
from dotenv import load_dotenv


load_dotenv()

dirs = os.listdir(datapth)


for d in dirs:
    files = os.listdir(d)
