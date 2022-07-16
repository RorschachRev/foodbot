import requests
import json
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
import sqlite3
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_Monroe.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
root.addHandler(handler)

# Create or verify SQLite DB
conn = sqlite3.connect('../testbots/db.il_monroe')
conn.execute('DROP TABLE IF EXISTS jsonfac')
conn.execute('DROP TABLE IF EXISTS jsoninsp')
conn.execute('CREATE TABLE IF NOT EXISTS jsonfac(facid test, json text)')
conn.execute('CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)')
print('DB Initialized')

if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	url='https://monroecountyhealth.org/home/environmental-health-foods/food-service-establishment-scores/'
	for trys in range(4):
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
	except Exception:
		logging.exception(('Exception3, Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
		print("Exception3")
	facility = {}
	inspec = {}
	inspections = {}
	for line in table.findAll('tr'):
		if not line.find('strong'):
			data = line.findAll('td')
			name=data[0].getText().strip()
			address=data[1].getText().strip()
			date=data[2].getText().strip()
			summary=data[3].getText().strip()
			facility['Name'] = name
			facility['Address'] = address
			inspec['Date'] = date
			inspec['Summary'] = ('Score: %s')%(summary)
			inspections[inspec['Date']] = inspec
			facility['Inspections'] = inspections
			inspections = {}
			print(facility)
			facid = json.dumps(name)
			reports = json.dumps(facility)
			cur = conn.cursor()
			cur.execute('select * from jsonfac where facid=:id', {'id':facid})
			get_one=cur.fetchone()
			if get_one is None:
				cur = conn.cursor()
				cur.execute('REPLACE INTO jsonfac VALUES (?,?)', (facid, reports))
				conn.commit()

conn.close()
print('Write successful, DB Closed')
