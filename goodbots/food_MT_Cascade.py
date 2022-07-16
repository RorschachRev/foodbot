import requests
import pickle
import logging
import logging.handlers

import sys,os,time
import html5lib
from bs4 import BeautifulSoup
import json
import sqlite3

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_MT_Cascade.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

#Create or verify SQLite DB File
conn = sqlite3.connect('../testbots/db.mt_cascade')
conn.execute("DROP TABLE IF EXISTS jsonfac")
conn.execute("DROP TABLE IF EXISTS jsoninsp")
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)")
#conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
#conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
#print("DB Created or Reset...")

if __name__ == '__main__':
	urls=[]
	for x in range(1,2000):#1,2000
		f=[]

		record_id = f'{x:07}'

		pageurl=('http://www.decadeonline.com/insp.phtml?agency=CAS&violsortfield=TB_CORE_INSPECTION_VIOL.VIOLATION_CODE&record_id=PR%s')%(record_id)
		for tries in range(2):
			try:
				page=requests.get(pageurl)
				#print("Try " + record_id)
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Exception1, Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
				#print("Exception1")
				time.sleep(3)
			except Exception:
				logging.exception(("Exception2, Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
				#print("Exception2")

		#url = ('http://www.decadeonline.com/insp.phtml?agency=CAS&violsortfield=TB_CORE_INSPECTION_VIOL.VIOLATION_CODE&record_id=PR0000002')
		#page=requests.get(url)

		try:
			soup=BeautifulSoup(page.text,'html5lib')

		except Exception:
			logging.exception(("Exception3, Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  soup) )
			#print('Exception3')

		#Table holds all inspection info
		table = soup.findAll('table')
		#Table2 specifically holds facility info
		try:
			table2 = table[2]
			label1 = table2.findAll('td')[0].getText().strip()
			program = table2.findAll('td')[1].getText().strip()
			label2 = table2.findAll('td')[2].getText().strip()
			facility_name = table2.findAll('td')[3].getText().strip()
			label4 = table2.findAll('td')[4]
			map = label4.find('a')['href']
			label3 = table2.findAll('td')[5].getText().strip()
			address = table2.findAll('td')[6].getText().strip()


			#-----------------------------------------------------
			count = 1
			count2 = 1
			count3 = 1
			x=4
			y=2
			facility={}
			inspections={}

			for x in range(4,len(table)):
				data2 = table[x].findAll('td')
				entry={}
				summary={}
				date = data2[0].getText().strip()[0:10]
				type = table[4].findAll('strong')[0].getText().strip()
				#summary['Date'] = date

				summary['inspec_title'] = type
				z=1
				#fill entry(dict) with inspection data from the site
				try:
					for y in range(2,len(data2), 2):
						summary['entry_title' + str(z)] = data2[y-1].getText().strip()#(1...)
						summary['entry_text' + str(z)] = data2[y].findAll('span')[0].getText().strip()#(2...)
						z += 1
				except:
					summary['entry_title' + str(z)] = 'No Violations Observed.'
					summary['entry_text' + str(z)] = ''
					#print('End of index or no entries present.')
					pass
					z += 1
				entry['Date'] = date
				entry['Summary'] = summary
				inspections[str(date)] = entry
				if count <= (len(table)):
					count += 1

			facility['Name'] = facility_name
			facility['Address'] = address
			facility['Map'] = map
			facility['Inspections'] = inspections

			facinfo = json.dumps(facility)
			#print(facinfo)
			#-----------------------------------------------------


			facid = json.dumps(facility['Name'])
			#reports = json.dumps(inspec)
			facility.pop('Name')
			facinfo = json.dumps(facility)

			cur= conn.cursor()
			cur.execute("select * from jsonfac where facid=:id", {"id":facid})
			get_one=cur.fetchone()  #named after redis "get"
			if get_one is None:  #suspend and resume - if we have no data, then get it!
				cur= conn.cursor()
				#Write to DB
				#print("Writing to DB...")
				cur.execute("REPLACE INTO jsonfac VALUES (?,?)", (facid, facinfo)) #insert location into jsonfac
				conn.commit()

		except:
			#print('No data for record_id, moving on...')
			pass

	conn.close()
	#print("Write successful, DB Closed.")

#print("Page " + record_id + " Was tried...")
