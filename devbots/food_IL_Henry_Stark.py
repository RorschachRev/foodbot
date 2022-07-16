import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_Henry_Stark.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	#~ queryset=['B'] test queryset
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	inspecturls=[]
	for val in queryset:
		url=''
		data=False
		pageurl=('https://healthspace.com/clients/illinois/henrystark/web.nsf/Food-List-ByFirstLetterInName?OpenView&Count=35&RestrictToCategory=%s')%(val)
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
			data=soup.findAll('table')[1]
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			a=data.findAll('a')
			for value in a:
				href=value['href'].strip()
				url=('https://healthspace.com%s')%(href)
				inspecturls.append(url)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for line in inspecturls:
		data={}
		inspections={}
		inspection=[]
		data['FacID']=line.split('=')[1]
		if(r.get( ('canIL_Henry_Stark_fac_%s')%(data['FacID']) )):
			print("Data exists:", data['FacID'])
			continue
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
			soup=BeautifulSoup(page.text,'html.parser')
			tables=soup.findAll('table')
			details=tables[0].findAll('td')
			name=details[1].getText().strip()
			data['FacName']=name
			data['Address']=details[3].getText().strip()
			details=tables[1].findAll('td')
			data['Phone']=details[5].getText().strip()
			data["FacType"]=details[1].getText().strip()
			data['Risk Rating']=details[3].getText().strip()
			if(tables[4].text.__contains__('Inspection Type') ):
				inspection=tables[4].findAll('td')
			if(tables[5].text.__contains__('Inspection Type') ):
				inspection=tables[5].findAll('td')
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )
		for val in range(0, inspection.__len__(), 3):
			try:
				inspec={}
				inspec['InspType']=inspection[val].getText().strip()
				x=inspection[val].find('a')['href']
				inspec['InspURL']=('https://healthspace.com/Clients/Illinois/HenryStark/Web.nsf/%s')%(x)
				date=inspection[val+1].getText().strip()
				inspec['InspDate']=date
				inspec['InspectID']= x.split("=")[1]
				inspec['InspSummary']=inspection[val+2].getText().strip()
				inspections[date]=inspec
			except Exceptions:
				logging.exception(("Unexpected error: %s reader was trying to parse inspections: %s")%(sys.exc_info()[0] ,  val) )
		data['Inspections']=inspections
		r.set(('canIL_Henry_Stark_fac_%s')%(data['FacID']), pickle.dumps(data))