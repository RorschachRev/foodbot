import json
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis
import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_Chicago.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	try:
		r = redis.StrictRedis(host='localhost', port=6379, db=0)
		driver=webdriver.Firefox()
		url='https://data.cityofchicago.org/Health-Human-Services/Food-Inspections/4ijn-s7e5/data'
		driver.get(url)
		driver.implicitly_wait(2)
		while driver.find_element_by_class_name('pager-button-next').is_enabled():
			table=driver.find_element_by_css_selector('table').get_attribute('outerHTML')
			soup=BeautifulSoup(table, 'html.parser')
			tbody=soup.find('tbody').findAll('tr')
			for item in tbody:
				bizdata={}
				inspdata={}
				info=item.findAll('td')
				inspectionid=info[0].text.strip()
				licenseid=info[3].text.strip()
				keyname=('canIL_Chicago_%s')%(licenseid)
				inspdata['InspectID']=inspectionid
				bizdata['bizname']=info[1].text.strip()
				bizdata['altbizname']=info[2].text.strip()
				bizdata['licenseid']=licenseid
				bizdata['FacType']=info[4].text.strip()
				bizdata['risklevel']=info[5].text.strip()
				bizdata['address']=info[6].text.strip()
				bizdata['city']=info[7].text.strip()
				bizdata['state']=info[8].text.strip()
				bizdata['ZIP']=info[9].text.strip()
				inspdata['InspDate']=info[10].text.strip()
				inspdata['InspType']=info[11].text.strip()
				inspdata['InspResult']=info[12].text.strip()
				inspdata['InspViol']=info[13].text.strip()
				if r.keys(keyname):
					key=pickle.loads(r.get(keyname))
					key['inspections'][inspectionid]=inspdata
					r.set(keyname,pickle.dumps(key))
				else:
					bizdata['inspections']={}
					bizdata['inspections'][inspectionid]=inspdata
					r.set(keyname,pickle.dumps(bizdata))
			driver.find_element_by_class_name('pager-button-next').click()
		
		table=driver.find_element_by_css_selector('table').get_attribute('outerHTML')
		soup=BeautifulSoup(table, 'html.parser')
		tbody=soup.find('tbody').findAll('tr')
		for item in tbody:
			bizdata={}
			inspdata={}
			info=item.findAll('td')
			inspectionid=info[0].text.strip()
			licenseid=info[3].text.strip()
			keyname=('canIL_Chicago_%s')%(licenseid)
			inspdata['InspectID']=inspectionid
			bizdata['bizname']=info[1].text.strip()
			bizdata['altbizname']=info[2].text.strip()
			bizdata['licenseid']=licenseid
			bizdata['FacType']=info[4].text.strip()
			bizdata['risklevel']=info[5].text.strip()
			bizdata['address']=info[6].text.strip()
			bizdata['city']=info[7].text.strip()
			bizdata['state']=info[8].text.strip()
			bizdata['ZIP']=info[9].text.strip()
			inspdata['InspDate']=info[10].text.strip()
			inspdata['InspType']=info[11].text.strip()
			inspdata['InspResult']=info[12].text.strip()
			inspdata['InspViol']=info[13].text.strip()
			if r.keys(keyname):
				key=pickle.loads(r.get(keyname))
				key['inspections'][inspectionid]=inspdata
				r.set(keyname,pickle.dumps(key))
			else:
				bizdata['inspections']={}
				bizdata['inspections'][inspectionid]=inspdata
				r.set(keyname,pickle.dumps(bizdata))
	except Exception:
		logging.error(('Unexpected error using foodbot_IL_Chicago %s')%(sys.exc_info()[0]))
	driver.quit()