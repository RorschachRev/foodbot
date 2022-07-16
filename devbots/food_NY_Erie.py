import requests
import pickle
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import sqlite3
import json

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_NY_Erie.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

# Create or verify SQLite DB
conn = sqlite3.connect('../testbots/db.ny_erie')
conn.execute('DROP TABLE IF EXISTS jsonfac')
conn.execute('DROP TABLE IF EXISTS jsoninsp')
conn.execute('CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)')
conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)')
print('DB Initialized')

if __name__ == '__main__':
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	inspecturls=[]
	for val in queryset:
		url=''
		data=False
		pageurl=('https://www.healthspace.com/Clients/NewYork/Erie/Erie_Live_Web.nsf/Food-List-ByFirstLetterInName?OpenView&Count=1000&RestrictToCategory=%s')%(val)
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
	for line in inspecturls:
		data={}
		inspections={}
		inspection={}
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
				x=inspection[val].find('a')['href']
				inspec['InspURL']=('https://www.healthspace.com/Clients/NewYork/Erie/Erie_Live_Web.nsf/%s') % (x)
				inspec['InspectID']= x.split("=")[1]
				inspec['Date']=inspection[val+1].getText().strip()
				inspec['Summary']=inspection[val+2].getText().strip()
				inspections[inspection[val+1].getText().strip()] = inspec
			except:	
				#~ print(inspection[val])
				logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )
		data['Inspections']=inspections
		print(data)
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
