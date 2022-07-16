import requests
import pickle
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import sqlite3
import json


"""
WRITE-ME!
ModLog
Date:				User:						Mod/Note:
3/25/19				David						Works but does not retrieve actual inspections, only links to the inspection.



"""

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "../../logs/food_AZ_Yavapai.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

# Create or verify SQLite DB
conn = sqlite3.connect('../../testbots/db.az_yavapai2')
conn.execute('DROP TABLE IF EXISTS jsonfac')
conn.execute('DROP TABLE IF EXISTS jsoninsp')
conn.execute('CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)')
conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)')
print('DB Initialized')

if __name__ == '__main__':
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	inspecturls=[]

	url=''
	data=False

	pageurl=('https://www.healthspace.com/clients/Arizona/Yavapai/Yavapai_Web_Live.nsf/Food-ByInspectionDate?OpenView&Count=2000')
	for tries in range(4):
		try:
			page=requests.get(pageurl)
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
	print(len(inspecturls))	#to find out how many records we matched
	#print(inspecturls)
	#inspecturls=[]	#we don't want to run the normal loop, turn off to process inspections
	for line in inspecturls:
		data={}
		inspections={}
		inspection={}
		for tries in range(2):
			try:
				page=requests.get(line)
				logging.debug(line)
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
			#if(details[3].text.__contains__('Phone Number') ):
			#	data['Phone']=details[3].getText().strip()
			data['FacType']=details[1].getText().strip()
			data['Map']=soup.find("a")['href']
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

				inspec['InspURL']=('https://www.healthspace.com/clients/Arizona/Yavapai/Yavapai_Web_Live.nsf/%s') % (x)
				inspec['InspectID']= x.split("=")[1]
				inspec['Date']=inspection[val+1].getText().strip()
				inspec['Summary']=inspection[val+2].getText().strip()
				inspections[inspection[val+1].getText().strip()] = inspec
			except:
				print(inspection[val])
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
