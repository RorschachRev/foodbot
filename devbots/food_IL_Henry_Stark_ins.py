import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import html5lib

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_Henry_Stark_insp.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for temp in r.keys('canIL_Henry_Stark_fac_*'):
		key=pickle.loads(r.get(temp))
		for inspection in key['Inspections']:
			for tries in range(4):
				try:
					page=requests.get(key['Inspections'][inspection]['InspURL'])
					break
				except (ConnectionError, ConnectionResetError):
					logging.exception(('Connection error was trying to get %s')%(inspection['Link']))
					time.sleep(3)
				except Exception:
					logging.exception(('Unexpected error: %s was trying to get: %s')%(sys.exc_info()[0],inspection['Link']))
			if r.keys(('canIL_Henry_Stark_ins_%s')%(key['Inspections'][inspection]['InspectID'])):
				continue
			try:
				soup=BeautifulSoup(page.text,'html5lib')
				items=soup.findAll('div', {"class": 'tabItem'} )
				noncrit=items[0].find('div',{"id":"manager"}).text.strip()
				crit=items[0].find('div',{"id":"general"}).text.strip()
				details=items[3].text.strip().replace('\n','<br>')
				info={}
				info['InspCrit']=crit.replace('\n','<br>')
				info['InspNonCrit']=noncrit.replace('\n','<br>')
				info['InspDetails']=details.replace('\t','<p>')
				r.set(('canIL_Henry_Stark_ins_%s')%(key['Inspections'][inspection]['InspectID']), pickle.dumps(info))
			except Exception:
				logging.exception(('Unexpected error: %s was trying to parse: %s')%(sys.exc_info()[0],soup))