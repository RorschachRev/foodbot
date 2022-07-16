import requests
import pickle
from bs4 import BeautifulSoup
import logging
import logging.handlers
import redis
import sys,os,time

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_ID_PanhandleHD1.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	url='http://www2.phd1.idaho.gov/Foodsearch/foodsearch.asp#'
	table=''
	for tries in range(4):
		try:
			page=requests.post(url,{'txtname':''})
			break
		except (ConnectionError, ConnectionResetError):
			logging.exception(("Connection error was trying to get: %s and trying: %s")%(url,str(tries)))
			time.sleep(3)
		except Exception:
			logging.exception(("Unexpected error: %s was trying to get: %s")%(str(sys.exe_info()[0]),url))
			break
	try:
		soup=BeautifulSoup(page.text, 'html.parser')
		
	for row in table:
		bizinfo={'id':'','Name':'','Address':'','Violations':'','Inspections':''}
		#check if food related
		#save id biz name address and violations to bizinfo
		#Click to go to biz details
		#save inspections to inspections
		r.set(('ID_PanhandleHD1_%s')%(bizinfo[id]), pickle.dumps(bizinfo))