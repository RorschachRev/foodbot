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
    os.environ.get("LOGFILE", "../logs/food_IL_Pike.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

#Create or verify SQLite DB File
conn = sqlite3.connect('../testbots/db.il_pike')
conn.execute("DROP TABLE IF EXISTS jsonfac")
conn.execute("DROP TABLE IF EXISTS jsoninsp")
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid text, json text)")
#conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
#conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
print("DB Created or Verified...")

if __name__ == '__main__':

	url='https://www.pikecountyil.org/health-department/restaurant-inspection-scores/'
	for trys in range(4):
		try:
			page=requests.get(url)
			logging.debug(('page got %s')%(url))
			break
		except (ConnectionError, ConnectionResetError):
			logging.exception(("Connection error reader was trying to get: %s and trying: %s")%(url, tries))
			time.sleep(3)
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to get: %s")%(sys.exc_info()[0], url))
	try:
		soup=BeautifulSoup(page.text,'html.parser')
		table=soup.find('table')
		info=table.findAll('tr')
	except Exception:
		logging.exception(('Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
	for val in range(1, info.__len__()):
		data={}
		inspec={}
		inspections={}
		line=info[val].findAll('td')
		name=line[0].getText().strip()
		data['Name']=name
		data['Address']=line[1].getText().strip()
		FBRiskFactors = line[4].getText().strip() #FB = Foodborne Illness
		GRPRiskFactors = line[5].getText().strip() #GRP = Good Retail Practices

		inspec['Date']=line[2].getText().strip()
		inspec['Summary'] = "Food-Borne Illness Risk Factors: " + FBRiskFactors + " Good Retail Practices: " + GRPRiskFactors

		inspections[inspec['Date']] = inspec
		data['Inspections'] = inspections

		facid = json.dumps(data['Name'])
		data.pop('Name')
		reports = json.dumps(data)
		print(data['Inspections'])

		cur= conn.cursor()
		cur.execute("select * from jsonfac where facid=:id", {"id":facid})
		get_one=cur.fetchone()  #named after redis "get"
		if get_one is None:  #suspend and resume - if we have no data, then get it!
			cur= conn.cursor()
			#Write to DB
			print("Writing to DB...")
			cur.execute("REPLACE INTO jsonfac VALUES (?,?)", (facid, reports)) #insert location into jsonfac
			#jsoninspect = []
			#for inspect in jsoninspect: #This actually gets built during parsing. read/write to the database in as short a duration as possible.
			#   jsoninspect.append((inspect)) #Add items
			#cur.executemany('REPLACE INTO jsoninsp VALUES (null, ?)', (reports))
			conn.commit()


conn.close()
print("Write successful, DB Closed.")
