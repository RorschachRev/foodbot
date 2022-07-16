import requests
import json
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_Chicago.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	start=0
	length=50
	pageurl=('https://data.cityofchicago.org/views/INLINE/rows.json?accessType=WEBSITE&method=getByIds&asHashes=true&start=%s&length=%s&meta=true&$order=inspection_date')%(start, length)
	try:
		for tries in range(4):
			try:
				page=requests.get(pageurl)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
	try:
		soup=BeautifulSoup(page.text, 'html.parser')
		