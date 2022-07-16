import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "logs/food_NY_Erie.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	#~ queryset=['B']  #test queryset
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	inspecturls=[]
	for val in queryset:
		url=''
		data=False
		#WARNING TODO: limited to 50 responses.
		#http://www.decadeonline.com/results.phtml?agency=trc&offset=50&businessname=s&sort=FACILITY_NAME&startswith=ON	#note: this is a different link than on the page
		offset=0
			
		#if(page.text.__contains__("Next Page") ) : #TODO continue with the next 50, incrementing the offset in a loop.
		
		for tries in range(4):
			try:
				pageurl=('http://www.decadeonline.com/results.phtml?agency=trc&offset=0&businessname=%s&sort=FACILITY_NAME&startswith=ON')%(val)
				while(page.text.__contains__("Next Page")):
					offset= offset+50
					pageurl=('http://www.decadeonline.com/results.phtml?agency=trc&offset=%s&businessname=%s&sort=FACILITY_NAME&startswith=ON')%(offset, val)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
		try:
			soup=BeautifulSoup(page.text,'html5lib')
			#TODO: get a list of all links inside target table
			data=soup.findAll('table')[2]
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			a=data.findAll('a')
			for value in a:
				href=value['href'].strip()
				url=('https://healthspace.com%s')%(href)
				inspecturls.append(url)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	#~ inspecturls=['http://www.decadeonline.com/insp.phtml?agency=trc&violsortfield=TB_CORE_INSPECTION_VIOL.VIOLATION_CODE&record_id=PR0003097']
	for line in inspecturls:
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
			tables=soup.findAll('table')
			details=tables[0].findAll('td')
			data['FacID']=line.split("=")[1] 
			if(r.get( ('canNY_Erie_fac_%s')%(data['FacID']) )):
				print("Data exists:", data['FacID'])
				continue
			data['Name']=details[1].getText().strip()
			data['Address']=details[3].getText().strip()
			details=tables[1].findAll('td')
			data['Phone']=details[3].getText().strip()
			data['FacType']=details[1].getText().strip()	#Pool
			data['maplink']=soup.find("a")['href']
			if(tables[4].text.__contains__('Inspection Type') ):
				inspection=tables[4].findAll('td')
			if(tables[5].text.__contains__('Inspection Type') ):
				inspection=tables[5].findAll('td')
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )				
		for val in range(0, inspection.__len__(), 3):	#3 td elements per tr, but no </tr>
			try:
				inspec={}
				inspec['InspType']=inspection[val].getText().strip()
				#x was named sublink, but I don't want anyone to think it is stored or used.
				x=inspection[val].find('a')['href']
				inspec['InspURL']=('https://www.healthspace.com/Clients/NewYork/Erie/Erie_Live_Web.nsf/%s') % (x)
				inspec['InspectID']= x.split("=")[1]
				inspec['InspDate']=inspection[val+1].getText().strip()
				inspec['InspSummary']=inspection[val+2].getText().strip()
				inspections.append(inspec)
			except:	
				#~ print(inspection[val])
				logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )
		data['Inspections']=inspections
		r.set(('canNY_Erie_fac_%s')%(data['FacID']), pickle.dumps(data))
