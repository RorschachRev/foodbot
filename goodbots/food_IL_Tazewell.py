import requests
import pickle
import logging
import logging.handlers
import sys,os,time
from bs4 import BeautifulSoup
import sqlite3
import json

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_Tazewell.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

# Create or verify SQLite DB
conn = sqlite3.connect('../testbots/db.il_tazewell')
conn.execute('DROP TABLE IF EXISTS jsonfac')
conn.execute('DROP TABLE IF EXISTS jsoninsp')
conn.execute('CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)')
conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)')
print('DB Initialized')


if __name__ == '__main__':
	for permitID in range(1,2500):
		data={}
		inspections={}
		url=('http://il.healthinspections.us/tazewell/estab.cfm?permitID=%s#')%(permitID)
		for tries in range(4):
			try:
				page=requests.get(url)
				logging.debug(('page got %s')%(url))
				if page.text.__contains__('The service is unavailable.'):
					time.sleep(2)
					continue
				if page.status_code >= 500: 	#503 Service Unavailable
					time.sleep(2)
					continue
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error reader was trying to get: %s and trying: %s")%(url, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s reader was trying to get: %s")%(sys.exc_info()[0], url))
		try:
			soup=BeautifulSoup(page.text,'html.parser')
			table=soup.find('table').findAll('td')[1]
			info=table.findAll('div')
			data['Name']=info[1].find('b').getText().strip()
			text=info[1].find('i').getText().split('\r')
			try:
				data['Address']=('%s %s')%(text[1].strip(),text[3].strip())
			except Exception:
				logging.info(('%s is empty')%(url))
				continue
			val=2
		except Exception:
			logging.exception(('Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
			logging.debug(('%s') % (page.text) )
		try:
			while val < info.__len__():
				details=info[val].findAll('div')
				inspec={}
				date=details[1].getText().split('\n')[1].split(':')[1].strip()
				inspec['InspURL']=('https://il.healthinspections.us%s')%(details[0].find('a').get('href').split()[1])
				inspec['InspDemerits']=details[1].getText().split('\n')[7].strip()
				inspec['InspType']=details[1].getText().split('\n')[10].split(':')[1].strip()
				vio=[]
				for var in range(2, details.__len__() -1):
					vio.append(details[var].getText().strip())
				summary = ''.join(vio)
				inspec['Summary']=summary
				inspec['Date']=date
				inspections[date]=inspec
				val=val+details.__len__()
				if info[val].getText() == 'View Last 3 Inspections for this Establishment':
					break
		except Exception:
			logging.exception(('Unexpected error: %s was trying to parse inspections at %s')%(sys.exc_info()[0],url))
		data['Inspections']=inspections
		if data['Inspections']:
			facid = json.dumps(data['Name'])
			data.pop('Name')
			reports = json.dumps(data)
			print('Inspections found')
	
			cur = conn.cursor()
			cur.execute('select * from jsonfac where facid=:id', {'id':facid})
			get_one=cur.fetchone()
			if get_one is None:
				cur = conn.cursor()
				cur.execute('REPLACE INTO jsonfac VALUES (?,?)', (facid, reports))
				conn.commit()
conn.close()
print('Write successful, DB Closed.')
