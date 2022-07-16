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
 
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "foodbotdev.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
logs = logging.getLogger()
logs.setLevel(os.environ.get("LOGLEVEL", "INFO"))
logs.addHandler(handler)
 
if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	#for LicenseId in range(6722, 35000): #total time so far 142m
	for LicenseId in range(6720, 6724):
		license=[]
		biz=False
	#    print(LicenseId)
		url='https://secure.cdhd.idaho.gov/CDHPublic/License.aspx?LicenseId=' + str(LicenseId)
	#    print(url)
		#url='ashdfgajfblifgwaehfliasdgfjasdhfvak'
		license.append(url)
		logging.info(" " + url)
		try:
			page=requests.get(url)
		except Exception:
			logging.error("Unexpected error: "+ sys.exe_info()[0] + " Was trying to get: " + url)
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			exist = soup.find(id="ctl00_CPH1_lblTechMsg")
			if exist:
				r.set("ada"+str(LicenseId), pickle.dumps('error on page')
				
				logging.info(" license does not exist " + str(LicenseId))
			#test for childcare
			#test for revoked
				continue
		except Exception:
			logging.error("Unexpected error: "+ sys.exe_info()[0] + " Was trying to parse: " + url)
			
			
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
		r.set("ada"+str(LicenseId), pickle.dumps(license))

