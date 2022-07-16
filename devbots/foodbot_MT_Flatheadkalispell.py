import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import pickle
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_MT_Flatheadkalispell.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

if __name__ == '__main__':
	queryset=['a']#,'b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']
	urls=[]
	fac_page=[]
	for val in queryset:
		logging.info(val)
		data={}
		pageurl=(('http://www.inspectionsonline.us/MT/FlatheadKalispell/Inspect.nsf/SearchEstab?SearchView&Query=%s&SearchMax=0&SearchFuzzy=FALSE')%(val))
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
			soup = BeautifulSoup(page.text, 'html.parser')
			data = soup.findAll(target="_self")
			if data == False:
				logging.info(" Search failed " )
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			for value in data:
				url=value['href']
				fac_page.append(url.strip())
	
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	donekeys=r.keys('canMT_Flatheadkalispell_*')
	logging.info(("donekeys has %s entries")%(donekeys.__len__()))
	print(("donekeys has %s entries") % (donekeys.__len__() ) )
	
	fac_page = ['/MT/FlatheadKalispell/Inspect.nsf/vw_InspectionsPubSumm?OpenView&RestrictToCategory=E8447DD8E35A4CFA8725740F0057C3A8']
	for line in fac_page:
		bizid=str(line).split('=')[1].strip()  #Get bizid from line fragment for redis key
		keyname=('canMT_Flatheadkalispell_%s')%(bizid)
#		if  donekeys.__contains__(keyname.encode("utf-8")):
#			continue
#		else:
#			logging.info(('Getting data for %s')%(bizid))
		facility={}
		inspections ={}
		records=None
		inspectid=''
		line=line.strip()
		for tries in range(4):
			try:
				page=requests.get(('http://www.inspectionsonline.us%s')%(line))
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
			facility = soup.find('table',{'class':'gt'})
			print(soup)
#			print(facility)
#			print(facility.find(id='EstabName'))
#			print(facility.find(id='Addr'))
#			for row in facility.findAll('td'):
#				print(dir(row))
#				print(row)
#			print(data['Name'])
			records = soup.find(id="vwTbl")
#			print(('PAGE:\n%sRECORDS:\n%s\n\nFACILITY:\n%s')%(page, records, facility))
			logging.debug('table found ' + str(records))
			if records == None:
				logging.info(" Search failed ")
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: http://www.inspectionsonline.us%s")%(sys.exc_info()[0] ,  line) )
		if records != None:
#			print(records.findAll())
			recordrow = records.findAll('tr')
#			print(recordrow)
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
				inspectdata['InspViol']=cell[2].text
				inspectdata['InspGrade']=cell[3].text
				
				inspections[inspectid]=inspectdata
				logging.info('inspections set')
			#parse table cells in each row
			#save text, recordid in row
			#add all data for each row to list or dictionary
			logging.debug('inspections is: ' + str(inspections))
			if inspections != {}:
#				print(inspections)
				#~ chips=pickle.dumps(inspections[inspectid])
				r.set('canMT_Flatheadkalispell_'+bizid, pickle.dumps(inspections[inspectid])) 
			#~ time.sleep(2)
		else:
			logging.warning(("No data found: %s soup: %s")%(line, soup) )
