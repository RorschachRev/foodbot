import requests
import pickle
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_MO_ClayLiberty_reader.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	f=open("MO_ClayLiberty_queryurl.txt")
	donekeys=r.keys('MO_ClayLiberty_reader_*')
	logging.info(("donekeys has %s entries")%(donekeys.__len__()))
	#~ logging.debug(("queryset has %s entries") % (queryset.__len__() ) )
	print(("donekeys has %s entries") % (donekeys.__len__() ) )
	#~ print(("queryset has %s entries") % (queryset.__len__() ) )
	
	for line in f:
	#~ for line in ['/ID/BonnevilleIdahoFalls/Inspect.nsf/vw_InspectionsPubSumm?OpenView&RestrictToCategory=FC9D653476B24CA486257A5A0052C173']:
		bizid=str(line).split('=')[1].strip()  #Get bizid from line fragment for redis key
		keyname=('MO_ClayLiberty_reader_%s')%(bizid)
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
				inspectdata['Type']=cell[0].text
				inspectdata['Date']=cell[1].text
				inspectdata['Vio']=cell[2].text
				inspectdata['Score']=cell[3].text
				
				inspections[inspectid]=inspectdata
				logging.info('inspections set')
			#parse table cells in each row
			#save text, recordid in row
			#add all data for each row to list or dictionary
			logging.debug('inspections is: ' + str(inspections))
			if inspections != {}:
				#~ chips=pickle.dumps(inspections[inspectid])
				r.set('MO_ClayLiberty_reader_'+bizid, pickle.dumps(inspections[inspectid])) 
			#~ time.sleep(2)
		else:
			logging.warning(("No data found: %s soup: %s")%(line, soup) )
	f.close()