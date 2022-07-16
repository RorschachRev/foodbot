import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import pickle
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_Id_bonneville.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	queryset=['A*', "B*","C*", 'D*','E*','F*','G*','H*','I*','J*','K*','L*','M*','N*','O*','P*','Q*','R*','S*','T*','U*','V*','W*','X*','Y*','Z*']
	#~ queryset=['A*',]
	urls=[]
	f=[]
	for val in queryset:
		data=False
		pageurl=('http://www.inspectionsonline.us/ID/bonnevilleidahofalls/Inspect.nsf/SearchEstab?SearchView&Query=[fld_Program]+CONTAINS+kw_Food+AND+([fld_EstabName]+CONTAINS+%s+OR+[fld_FaciName]+CONTAINS+%s)&SearchOrder=4&SearchWV=TRUE&SearchFuzzy=FALSE')%(val,val)
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
			logging.exception( ("Unexpected error: %s was trying to parse: %s")%( sys.exc_info()[0] ,  pageurl) )
		if data:
			for value in data:
				url=value['href']
				f.append(url.strip())
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	donekeys=r.keys('canID_bonneville_*')
	logging.info(("donekeys has %s entries")%(donekeys.__len__()))
	for line in f:
		bizid=str(line).split('=')[1].strip()
		keyname=('canID_bonneville_%s')%(bizid)
		if  donekeys.__contains__(keyname.encode("utf-8")):
			continue
		else:
			logging.info(('Getting data for %s')%(bizid))
		inspections ={}
		data=None
		inspectid=''
		line=line.strip()
		for tries in range(4):
			try:
				page=requests.get(('http://www.inspectionsonline.us%s')%(line))
				#~ page=requests.get('http://www.inspectionsonline.us/ID/BonnevilleIdahoFalls/Inspect.nsf/vw_InspectionsPubSumm?OpenView&RestrictToCategory=FFA3FC0F27CE252A8625778500685295')
				logging.debug(("page got http://www.inspectionsonline.us%s")%(line))
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error reader was trying to get: http://www.inspectionsonline.us%s and trying: %s")%(line, tries))
				time.sleep(3)
			#TODO: sleep 30 if name resolution error
			#~ except gaierror:
				#~ time.sleep(30)
			except Exception:
				logging.exception(("Unexpected error: %s reader was trying to get: http://www.inspectionsonline.us%s")%(sys.exc_info()[0], line))
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			data = soup.find(id="vwTbl")
			logging.debug('table found ' + str(data))
			if data == None:
				logging.info(" Search failed ")
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: http://www.inspectionsonline.us%s")%(sys.exc_info()[0] ,  line) )
		if data != None:
			recordrow = data.findAll('tr')
			logging.debug('recordrow set ' + str(recordrow))
			for row in recordrow:
				if row.find('th'):
					continue
				mylinks=row.findAll('a')
				for m in mylinks:
					inspectid=(m.__str__().split('"')[1].split('pUNID=')[1] )
					inspections[inspectid]=('http://www.inspectionsonline%s')%(line)
					logging.debug(('mylink %s obtained')%(m))
				#~ for val in range(1, recordrow.__len__()+1):#make a loop of every row 
				cell = row.findAll('td')
				logging.debug('cell set ' + str(cell))
				inspectdata={}
				inspectdata['InspType']=cell[0].text
				inspectdata['InspDate']=cell[1].text
				inspectdata['InspVio']=cell[2].text
				inspectdata['ScoreRF']=cell[3].text
				inspectdata['ScoreGRP']=cell[4].text
				
				inspections[inspectid]=inspectdata
				logging.info('inspections set')
			#parse table cells in each row
			#save text, recordid in row
			#add all data for each row to list or dictionary
			logging.debug('inspections is: ' + str(inspections))
			if inspections != {}:
				#~ chips=pickle.dumps(inspections[inspectid])
				r.set('canID_bonneville_'+bizid, pickle.dumps(inspections[inspectid])) 
			#~ time.sleep(2)
		else:
			logging.warning(("No data found: %s soup: %s")%(line, soup) )

