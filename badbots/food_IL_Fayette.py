import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup
import sqlite3

#on first run only, create new tables in new db if they don't exist, otherwise continue to next event
conn = sqlite3.connect('db.id_ada')
conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid, json text)")
conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
print("DB Created or Verified...")


print("Getting data now...")
handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_IL_Fayette.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	url='http://fayettehealthdept.org/eh_foodestablishmentscores.html'
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
		print("Parsing data now...")
		soup=BeautifulSoup(page.text, 'html.parser')
		table=soup.find("div", {"id": "e29"})
		content=table.find('tr').findAll('tr')
		for val in range(6,content.__len__()):
				data={}
				info=content[val].findAll('td', style='border:1px inset #DCDCDC')
				if info and info[4].text.strip(): #the part after the and lets it only set keys for locations that have an inspection under their new food code
					data['name']=info[0].getText().strip()
					data['RF/IV']=info[1].getText().strip() # RF/IV = risk factor/intervention violations
					data['repeat']=info[2].getText().strip()
					data['GRP']=info[3].getText().strip() #GRP = Good Retail Practices
					data['Insp_date']=info[4].getText().strip()
					#r.set(('IL, Fayette,%s')%(data['name']),pickle.dumps(data))

					#TEST Data
					'''data['name']="McDonald\'s"
					data['RF/IV']="1" # RF/IV = risk factor/intervention violations
					data['repeat']="2"
					data['GRP']="3" #GRP = Good Retail Practices
					data['Insp_date']="3/8/2019"'''

					facdata = "{\"RF/IV\":" + "\"" + data['RF/IV'] + "\", " + "\"Repeat\":" + "\"" + data['repeat'] + "\", " + "\"GRP\":" + "\"" + data['GRP'] + "\", " + "\"Insp Date\":" + "\"" + data['Insp_date'] + "\"}" #Construct a string variable with all insp data
					facid = data['name']

					cur= conn.cursor()
					cur.execute("select * from jsonfac WHERE facid=:id", {"id":facid})
					get_one=cur.fetchone()  #named after redis "get"
					if get_one is None:  #suspend and resume - if we have no data, then get it!
					    #runbot(url)  #What does this do???
						print("Writing to DB...")
						cur.execute("INSERT INTO jsonfac VALUES (?,?)", (facid, facdata)) #insert description into jsonfac
						jsoninspect = [] #Array called jsoninspect?
						for inspect in jsoninspect: #This actually gets built during parsing. read/write to the database in as short a duration as possible.
						   jsoninspect.append((insp_id, facdata)) #Add items
						cur.executemany('INSERT INTO jsoninsp VALUES (?,?)', ( jsoninspect))
						conn.commit()


					print("Printing...")
					print(facid)
					print(facdata, "\n")


	except Exception:
		logging.exception(('Exception3, Unexpected error: %s was trying to parse %s')%(sys.exc_info()[0],url))
		print("Exception3")
conn.close()
