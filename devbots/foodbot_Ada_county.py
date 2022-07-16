#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import json
import redis
import pickle
import logging
import logging.handlers
import os
import time
import sys
 
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/foodbot_ID_Ada.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
logs = logging.getLogger()
logs.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logs.addHandler(handler)
 
if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	#done for 1, 60000. Should do cache hit checks. Are we going to scrape every 2 weeks?
	for LicenseId in range(1, 60000):
	#for LicenseId in range(6720, 6724):
		license=[]
		biz=False
		if r.keys(("canID_ada_%s")%(LicenseId)):
			continue
	#    print(LicenseId)
		url='https://secure.cdhd.idaho.gov/CDHPublic/License.aspx?LicenseId=' + str(LicenseId)
	#    print(url)
		#url='ashdfgajfblifgwaehfliasdgfjasdhfvak'
		license.append(url)
		logging.info(" " + url)
		for tries in range(4):
			try:
				page=requests.get(url)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception("Connection error was trying to get: "+ url + " and trying: " + str(tries))
				time.sleep(3)
			except Exception:
				logging.exception("Unexpected error: " + str(sys.exe_info()[0]) + " was trying to get: " + url)
				r.set("err_id_ada_" + str(LicenseID), sys.exe_info()[0])
				break
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			errexist = soup.find(id="ctl00_CPH1_lblTechMsg")
			if errexist:
				logging.info(" license does not exist " + str(LicenseId))
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  url) )
			r.set("err_id_ada_" + str(LicenseID), sys.exe_info()[0])
			
		biz=soup.find(id="ctl00_CPH1_TabBrowsePnl1")
		
		if biz:
			biz_data = [
				[input.get('value') for input in row("input")]
				for row in biz("tr")
			]
	#        for c in biz_data:
	#            print(c)
			license.append(biz_data)
			logging.info(biz_data)
		else:
			license.append(False)
			logging.info("no biz here: " + str(pickle.dumps(biz)))
		#logging.info(biz_data)
		inspections=soup.find(id='ctl00_CPH1_InspectionGrid')
		if inspections:
			inspection_data = [
					[td.getText().strip() for td in row('td')]
					for row in inspections('tr')              
			] 
	#        for c in inspection_data:
	#            print(c)
			license.append(inspection_data)
		else:
			license.append(False)
		r.set("canID_ada_"+str(LicenseId), pickle.dumps(license))

