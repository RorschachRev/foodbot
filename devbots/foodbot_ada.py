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
    os.environ.get("LOGFILE", "../logs/foodbot.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)
 
#try:
#    exit(main())
#except Exception:
#    logging.exception("Exception in main()")
#    exit(1)
if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for LicenseId in range(1, 35000): #total time so far 125m
	#for LicenseId in range(4, 5):
		if r.keys(("canID_ada_%s")%(LicenseId)):
			continue
		license=[]
		biz=False
	#    print(LicenseId)
		url='https://secure.cdhd.idaho.gov/CDHPublic/License.aspx?LicenseId=' + str(LicenseId)
	#    print(url)
		#url='ashdfgajfblifgwaehfliasdgfjasdhfvak'
		license.append(url)
		try:
			page=requests.get(url)
		except Exception:
			logging.exception("error pulling "+ url)
			exit(1)
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			biz=soup.find(id="ctl00_CPH1_TabBrowsePnl1")
		except Exception:
			logging.exception("error parsing "+ url)
		
		if biz:
			biz_data = [
				[input.get('value') for input in row("input")]
				for row in biz("tr")
			]
	#        for c in biz_data:
	#            print(c)
			license.append(biz_data)
		else:
			license.append(False)
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
