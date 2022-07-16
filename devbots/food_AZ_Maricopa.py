import requests
import pickle
#~ import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import sqlite3
import json

conn = sqlite3.connect('../db/db.AZ_Maricopa')
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid, json text)")
conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")


handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_AZ_Maricopa.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	for x in [01178,01179,01180,01177,01176,01175,01174,]:
	#~ for x in range(1,10000):
		#TODO Selenium, get facilities info http://envapp.maricopa.gov/EnvironmentalHealth/BusinessSearchResults/Mobile?z=85358&CuttingEdge=0
		line=('http://envapp.maricopa.gov/EnvironmentalHealth/BusinessInspectionResults/Mobile?p=FD-%s&i=0')%( x.zfill(5) )
		#OR (has captcha) https://envapp.maricopa.gov/EnvironmentalHealth/FoodInspections/Weekly?Length=15
		#OR https://envapp.maricopa.gov/EnvironmentalHealth/FoodGrade?d=03%2F03%2F2019&a=True (may be locked? has map address, name, etc. - best target?)
		#      https://envapp.maricopa.gov/EnvironmentalHealth/FoodGrade?d=02%2F03%2F2019&a=True
		#	Search by business	https://envapp.maricopa.gov/EnvironmentalHealth/FoodInspections/Business?Length=15
		#	by zip code: 	https://envapp.maricopa.gov/EnvironmentalHealth/BusinessSearchResults?z=85358&page=1
		data={}
		inspections=[]
		inspection=[]
		for tries in range(4):
			try:
				page=requests.get(line)
				logging.debug(line)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error reader was trying to get: %s and trying: %s")%(line, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s reader was trying to get: %s")%(sys.exc_info()[0], line))
		try:
			soup=BeautifulSoup(page.text,'html5lib')
			data['FacID']=line.split("=")[1].strip('&i')
			cur.execute("select * from jsonfac WHERE facid=:id", {"id":data['FacID']})
			get_one=cur.fetchone()  #named after redis "get"
			if get_one is None:  #suspend and resume - if we have no data, then get it!	for val in queryset:
				h2details=soup.findAll('h2')
				data['Name']=h2details[0].text
				h3details=soup.findAll('h3')
				data['Address']=h3details[1].text
				data['FacType']=h3details[0].text.split(':')[1].strip()
				data['FacURL']=line
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )				
		for val in range(0, inspection.__len__(), 3):	#3 td elements per tr, but no </tr>
			try:
				inspec={}
				inspec['Type']=inspection[val].getText().strip()
				#x was named sublink, but I don't want anyone to think it is stored or used.
				x=inspection[val].find('a')['href']
				inspec['Link']=('https://envapp.maricopa.gov/EnvironmentalHealth/FoodSearchInspection?p=%s&i=0') % (x)
				inspec['ID']= x.split("=")[1]
				inspec['Date']=inspection[val+1].getText().strip()
				inspec['Summary']=inspection[val+2].getText().strip()
				inspections.append(inspec)
			except:	
				#~ print(inspection[val])
				logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )
		data['Inspections']=inspections
		r.set(('canAZ_Maricopa_fac_%s')%(data['FacID']), pickle.dumps(data))
		#inspection link:	https://envapp.maricopa.gov/EnvironmentalHealth/FoodInspection?p=FD-04753&i=4436968