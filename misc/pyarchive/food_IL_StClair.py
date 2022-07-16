import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_IL_StClair.log"))
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
	url='http://www.health.co.st-clair.il.us/environmental/food/Documents/Copy%20of%20WebScores.htm'
	for tries in range(4):
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
		table=soup.find('table')
		info=table.findAll('tr')
		for val in range(1,info.__len__() - 2):
			data={}
			line=info[val].findAll('td')
			name=line[0].getText().strip()
			data['Name']=name
			data['Address']=line[1].getText().strip()
			data['City']=line[2].getText().strip()
			data['ZIP']=line[3].getText().strip()
			data['LastInspDate']=line[4].getText().strip()
			data['LastInspScore']=line[5].getText().strip()
			r.set(('IL_StClair_%s')%(name),pickle.dumps(data))
	except Exception:
		logging.exception(('Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))

		
