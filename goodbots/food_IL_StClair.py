import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup
import sqlite3
import json

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_StClair.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

#Create or verify SQLite DB File
conn = sqlite3.connect('../testbots/db.il_stclair')
conn.execute("DROP TABLE IF EXISTS jsonfac")
conn.execute("DROP TABLE IF EXISTS jsoninsp")
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)")

if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	url='http://www.health.co.st-clair.il.us/environmental/food/Documents/Copy%20of%20WebScores.htm'
	for tries in range(4):
		try:
			page=requests.get(url)
			logging.debug(('page got %s')%(url))
			break
		except (ConnectionError, ConnectionResetError):
			logging.exception(("Exception1, Connection error reader was trying to get: %s and trying: %s")%(url, tries))
			print("Exception1")
			time.sleep(3)
		except Exception:
			logging.exception(("Exception2, Unexpected error: %s reader was trying to get: %s")%(sys.exc_info()[0], url))
			print("Exception2")
	try:
		soup=BeautifulSoup(page.text,'html.parser')
		table=soup.find('table')
		info=table.findAll('tr')
		for val in range(1,info.__len__() - 2):
			data={}
			inspec={}
			inspections={}
			line=info[val].findAll('td')
			data['Name'] = name=line[0].getText().strip()
			Address = line[1].getText().strip()
			City = line[2].getText().strip()
			Zip = line[3].getText().strip()
			data['Address'] = Address + " City: " + City + " Zip: " + Zip

			inspec['Date']=line[4].getText().strip()
			inspec['Summary']=line[5].getText().strip()

			inspections[inspec['Date']] = inspec
			data['Inspections'] = inspections

			facid = json.dumps(data['Name'])
			data.pop('Name')
			reports = json.dumps(data)
			print(data['Inspections'])
			#print(facid)
			#print(reports)

			cur= conn.cursor()
			cur.execute("select * from jsonfac where facid=:id", {"id":facid})
			get_one=cur.fetchone()  #named after redis "get"
			if get_one is None:  #suspend and resume - if we have no data, then get it!
				cur= conn.cursor()
				#Write to DB
				print("Writing to DB...")
				cur.execute("REPLACE INTO jsonfac VALUES (?,?)", (facid, reports)) #insert location into jsonfac
				conn.commit()

	except Exception:
		logging.exception(('Exception3, Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
		print("Exception3")

conn.close()
print("Write successful, DB Closed.")
