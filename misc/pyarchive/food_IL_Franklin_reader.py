import requests
import pickle
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_IL_Franklin_reader.log"))
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
	f=open('IL_Franklin_queryurl.txt')
	for line in f:
		data={}
		inspections={}
		inspection=[]
		line=line.strip()
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
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )
		tables=soup.findAll('table')
		details=tables[0].findAll('td')
		name=details[1].getText().strip()
		data['Name']=name
		data['Address']=details[3].getText().strip()
		data['Phone']=tables[1].findAll('td')[3].getText().strip()
		inspection=tables[4].findAll('td')
		for val in range(0, inspection.__len__(), 3):
			inspec={}
			inspec['Type']=inspection[val].getText().strip()
			inspec['Link']=inspection[val].find('a')['href']
			date=inspection[val+1].getText().strip()
			inspec['Date']=date
			inspec['Summary']=inspection[val+2].getText().strip()
			inspections[date]=inspec
		data['Inspections']=inspections
		r.set(('IL_Franklin_%s')%(name), pickle.dumps(data))
	f.close()
		