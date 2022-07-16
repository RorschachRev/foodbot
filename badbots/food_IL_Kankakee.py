import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "logs/food_IL_Kankakee.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)
if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	closed={}
	for val in range(3000):
		if closed[val]:
			continue
		url=('http://il.healthinspections.us/kankakee/estab.cfm?facilityID=%s')%(val)
		for trys in range(4):
			try:
				page=requests.get(url)
				logging.debug(('page got %s')%(url))
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error reader was trying to get: %s and trying: %s")%(url, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s reader was trying to get: %s")%(sys.exc_info()[0], url))
		try:
			soup=BeautifulSoup(page.text,'html.parser')
		except Exception:
			logging.exception(('Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
		# They put everything in div tags