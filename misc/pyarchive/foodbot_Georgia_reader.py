import requests
import pickle
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_Georgia_reader.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	f=open('GA_queryurl.txt')
	donekeys=r.keys('GA_reader_*')
	#~ donetodo=r.keys('TODO_GA_*')
	logging.info(('donekeys has %s entries')%(donekeys.__len__()))
	print(("donekeys has %s entries") % (donekeys.__len__() ) )
	
	for line in f:
		bizid=str(line.split('=')[1]).strip()
		keyname=('GA_reader_%s')%(bizid)
		#~ todokeyname=('TODO_GA_%s')%(bizid)
		if  donekeys.__contains__(keyname.encode("utf-8")):
			#~ if not donetodo.__contains__(todokeyname.encode('utf-8')):
			continue
			#~ else
				#~ logging.info(('%s is already done, but had unfinished inspections')%(bizid))
		else:
			logging.info(('Getting data for %s')%(bizid))
		inspections={}
		data=None
		inspecturl=''
		inspectid=''
		line=line.strip()
		for tries in range(4):
			try:
				page=requests.get(('http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				logging.debug(('page got http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				time.sleep(1.5)
				break
			except (ConnectionError,ConnectionResetError):
				logging.exception(('Connection error reader was trying to get: http://ga.healthinspections.us/gwinnett_new/%s and trying %s')%(line,tries))
				time.sleep(3)
			except Exception:
				logging.exception(('Unexpected error: %s reader was trying to get: http://ga.healthinspections.us/gwinnett_new/%s')%(sys.exc_info[0],line))
		try:
			for tries in range(4):
				soup = BeautifulSoup(page.text, 'html.parser')
				if soup.text.__contains__("The service is unavailable."):
					logging.warning((' %s The service is unavailable')%(bizid))
					time.sleep(15)
					page=requests.get(('http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				else:
					break
			data=soup.find(bgcolor='#FFFFFF').find('div').findAll('table')	#TODO?: redo as td class="body"	
			#TODO if no table, save "No inspections found" as a list element to REDIS
			logging.debug('table found ' + str(data))
			logging.debug(data.__len__())
			if data == None:
				logging.info(" Search failed ")
				inspections[status]="No inspections found"
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: http://ga.healthinspections.us/gwinnett_new/%s")%(sys.exc_info()[0] ,  line) )
		if data!=None:
			for val in range(0,data.__len__(),2):
				inspectid=data[val].find('a').get('href').split("=")[1].split('&')[0]
				inspections[inspectid]={}
				a=data[val].find('a')
				inspecturl=a.get('href').strip('..')
				a=a.parent.find_next_sibling('td')
				inspectdate=a.getText().split(':')[1].strip()       
				a=a.find_next_sibling('td')
				inspections[inspectid]['Url']=inspecturl
				inspections[inspectid]['Date']=inspectdate
				inspectgrade=a.getText().split(':')[1].strip()
				inspections[inspectid]['Grade']=inspectgrade
				if not inspectgrade:
					later={}
					later['bizurl']=('http://ga.healthinspections.us/gwinnett_new/%s')%(line)
					later['inspecturl']=('http://ga.healthinspections.us%s')%(inspecturl)
					r.set(("TODO_GA_%s")%(bizid), pickle.dumps(later))
				Viol=data[val].find_next_sibling('table').findAll(bgcolor="efefef")
				if Viol:
					inspections[inspectid]['Violtable']={}
					for val in range(0, Viol.__len__()):
						inspections[inspectid]['Violtable'][val]={}
						table=Viol[val].findAll('td')
						inspections[inspectid]['Violtable'][val]['Violcode']=table[0].getText().strip()
						inspections[inspectid]['Violtable'][val]['ViolDesc']=table[1].getText().strip()
						inspections[inspectid]['Violtable'][val]['ViolOccur']=table[2].getText().strip()
		#TODO: If no "Grade:" we need to digest the actual report?
		logging.debug(("Inspections: %s")%(inspections))
		if inspections:	#This is why it is not writing... but I want you to figure out why not.
			r.set(('GA_reader_%s')%(bizid), pickle.dumps(inspections))
		else:
			logging.warning(('No data found: %s soup: %s')%(line, soup))
	f.close()