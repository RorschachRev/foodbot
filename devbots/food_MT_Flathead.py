#TODO 
#~  FacID exist but needs a little bit of work when it comes to the data
import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_MT_Flathead.log"))
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
		data=False
		pageurl=('http://www.inspectionsonline.us/MT/FlatheadKalispell/Inspect.nsf/SearchEstab?SearchView&Query=[fld_Program]+CONTAINS+kw_Food+AND+([fld_EstabName]+CONTAINS+%s+OR+[fld_FaciName]+CONTAINS+%s)&SearchOrder=4&SearchWV=TRUE&SearchFuzzy=FALSE')%(val,val)
		for tries in range(4):
			try:
				page=requests.get(pageurl)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
				#~ break
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			data = soup.findAll(target="_self")
			if data == False:
				logging.info(" Search failed " )
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			#~ a=data.findAll('a')
			#~ for value in a:
			for value in data:
				href=value['href'].strip()
				url=('https://inspectionsonline.us%s')%(href)
				inspecturls.append(url)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
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
			soup=BeautifulSoup(page.text,'html.parser')
			tables=soup.findAll('table')
			details=tables[0].findAll('td')
			data['FacID']=line.split("=")[1] 
			if(r.get( ('canMT_Flathead_fac_%s')%(data['FacID']) )):
				print("Data exists:", data['FacID'])
				continue
			data['Name']=details[1].getText().strip()
			data['Address']=details[3].getText().strip()
			details=tables[1].findAll('td')
			data['Phone']=details[3].getText().strip()
			data['FacType']=details[1].getText().strip()
			data['MapURL']=soup.find("a")['href']
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
				inspec['InspURL']=('http://www.inspectionsonline.us/ut/utahprovo/Inspect.nsf/%s') % (x)
				inspec['InspectID']= x.split("=")[1]
				inspec['InspDate']=inspection[val+1].getText().strip()
				inspec['InspSummary']=inspection[val+2].getText().strip()
				inspections.append(inspec)
			except:	
				#~ print(inspection[val])
				logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )
		data['Inspections']=inspections
		r.set(('canMT_Flathead_fac_%s')%(data['FacID']), pickle.dumps(data))