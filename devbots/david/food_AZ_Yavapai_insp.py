import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import html5lib

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_AZ_Yavapai_insp.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for temp in r.keys('canAZ_Yavapai_fac_*'):
		key=pickle.loads(r.get(temp))
		for inspection in key['Inspections']:
			for tries in range(4):
				try:
					page=requests.get(inspection['InspURL'])
					break
				except (ConnectionError, ConnectionResetError):
					logging.exception(('Connection error was trying to get %s')%(inspection['Link']))
					time.sleep(3)
				except Exception:
					logging.exception(('Unexpected error: %s was trying to get: %s')%(sys.exc_info()[0],inspection['Link']))
			if r.keys(('canNY_Erie_ins_%s')%(inspection['InspectID'])):
				continue
			try:
				soup=BeautifulSoup(page.text,'html5lib')
				tables=soup.findAll('table')
				info={}
				data=tables[1].findAll('tr')
				info['FacName']=data[1].findAll('td')[1].text.strip()
				info['FacType']=data[2].findAll('td')[1].text.strip()
				info['InspType']=data[3].findAll('td')[1].text.strip()
				info['InspDate']=data[3].findAll('td')[1].text.strip()
				violtable=tables[3].findAll('tr')
				violations=[]
				for viol in violtable:
					violations.append(viol.find('td').text.strip())
				info['Violations']=violations
				r.set(('canAZ_Yavapai_ins_%s')%(inspection['InspectID']), pickle.dumps(info))
			except Exception:
				logging.exception(('Unexpected error: %s was trying to parse: %s')%(sys.exc_info()[0],soup))
