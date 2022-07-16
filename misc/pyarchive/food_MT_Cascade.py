import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_MT_Cascade.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	urls=[]
	offset=0
	while (offset < 2000):
		pageurl=('http://www.decadeonline.com/results.phtml?agency=CAS&violsortfield=TB_CORE_INSPECTION_VIOL.UPDATE_BY&forceresults=1&offset=%s&businessname=&businessstreet=&city=&zip=&soundslike=&sort=FACILITY_NAME')%(offset)
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
			soup=BeautifulSoup(page.text,'html.parser')
			table=soup.findAll('table')[2].findAll('td')
			for item in table:
				link=('http://www.decadeonline.com/')%(item.find('a').get('href'))
				urls.append(link)
		offset=offset+50
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for url in urls:
		data={}
		data['Url']=url
		record_id=url.split('=')
		try:
			page=requests.get(url)
			break
		except (ConnectionError, ConnectionResetError):
			logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
			time.sleep(3)
		except Exception:
			logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
		try:
			soup=BeautifulSoup(page.text,'html.parser')
			tables=soup.findAll('table')
			