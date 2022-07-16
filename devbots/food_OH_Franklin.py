import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import redis
import pickle
import sqlite3

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_OH_Franklin.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

#Create or verify SQLite DB File
conn = sqlite3.connect('../testbots/db.oh_franklin')
conn.execute("DROP TABLE IF EXISTS jsonfac")
conn.execute("DROP TABLE IF EXISTS jsoninsp")
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)")
#conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
#conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
print("DB Created or Reset...")

if __name__ == '__main__':
	#~ queryset=['1'] #test queryset
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	f=[]
	for val in queryset:
		url=''
		data=False
		pageurl=('https://www.healthspace.com/Clients/Ohio/Franklin/Franklin_Web_Live.nsf/Food-List-ByFirstLetterInName?OpenView&Count=1000&RestrictToCategory=%s')%(val)
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
				href=value['href']
				url=('https://www.healthspace.com%s')%(href)
				f.append(url.strip())

	#r = redis.StrictRedis(host='localhost', port=6379, db=0)
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
		print(data)

		facid = json.dumps(data['Name'])
		#reports = json.dumps(inspec)
		data.pop('Name')
		facinfo = json.dumps(data)

		cur= conn.cursor()
		cur.execute("select * from jsonfac where facid=:id", {"id":facid})
		get_one=cur.fetchone()  #named after redis "get"
		if get_one is None:  #suspend and resume - if we have no data, then get it!
			cur= conn.cursor()
			#Write to DB
			print("Writing to DB...")
			cur.execute("REPLACE INTO jsonfac VALUES (?,?)", (facid, facinfo)) #insert location into jsonfac
			#For inspection details
			#jsoninspect = []
			#for inspect in jsoninspect: #This actually gets built during parsing. read/write to the database in as short a duration as possible.
			#   jsoninspect.append((insp_id, reports)) #Add items
			#cur.executemany('REPLACE INTO jsoninsp VALUES (?, ?)', ( jsoninspect))
			conn.commit()
		#print(fac_id, "\n", fac_data)
conn.close()
print("Write successful, DB Closed.")
