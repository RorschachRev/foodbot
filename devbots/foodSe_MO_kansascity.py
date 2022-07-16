import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import redis
import sqlite3
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/foodSe_MO_kansascity.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	conn = sqlite3.connect('../db/db.foodbot_MO_kansascity')
	conn.execute("CREATE TABLE  IF NOT EXISTS jsonfac(facid text, json text)")
	conn.execute("CREATE TABLE  IF NOT EXISTS jsoninsp(inspid text, json text)")
	conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
	conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
	queryset=['A*', "B*","C*", 'D*','E*','F*','G*','H*','I*','J*','K*','L*','M*','N*','O*','P*','Q*','R*','S*','T*','U*','V*','W*','X*','Y*','Z*']
	#~ queryset=['A*',]
	urls=[]
	f=[]
	for val in queryset:
		data=False
		pageurl=('http://www.inspectionsonline.us/MO/USAKansasCity/Inspect.nsf/SearchEstab?SearchView&Query=[fld_Program]+CONTAINS+kw_Food+AND+([fld_EstabName]+CONTAINS+%s+OR+[fld_FaciName]+CONTAINS+%s)&SearchOrder=4&SearchWV=TRUE&SearchFuzzy=FALSE')%(val,val)
		for tries in range(4):
			try:
				page=requests.get(pageurl)
				break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
				#~ break
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			data = soup.findAll(target="_self")
			if data == False:
				logging.info(" Search failed " )
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s")%(sys.exc_info()[0] ,  pageurl) )
		if data:
			for value in data:
				url=value['href']
				f.append( url.strip())
	driver=webdriver.Firefox()
	driver.implicitly_wait(2)
	for line in f:
		bizid=str(line).split('=')[1].strip()
		#~ keyname=('canMO_Kansascity_%s')%(bizid)
		c = conn.cursor()
		c.execute("select * from jsonfac where facid=:id", {"id":bizid})
		get_one=c.fetchone()
		if  get_one is None:
			inspections ={}
			data=None
			inspectid=''
			line=line.strip()
			for tries in range(4):
				try:
					driver.get(('http://www.inspectionsonline.us%s')%(line))
					page=requests.get(('http://www.inspectionsonline.us%s')%(line))
					logging.debug(("page got http://www.inspectionsonline.us%s")%(line))
					break
				except (ConnectionError, ConnectionResetError):
					logging.exception(("Connection error reader was trying to get: http://www.inspectionsonline.us%s and trying: %s")%(line, tries))
					time.sleep(3)
				#TODO: sleep 30 if name resolution error
				#~ except gaierror:
					#~ time.sleep(30)
				except Exception:
					logging.exception(("Unexpected error: %s reader was trying to get: http://www.inspectionsonline.us%s")%(sys.exc_info()[0], line))
			try:
				data = driver.find_element_by_id('vwTbl')
				soup=BeautifulSoup(page.text, 'html.parser')
				logging.debug('table found ' + str(data))
				if data == None:
					logging.info(" Search failed ")
			except Exception:
				logging.exception(("Unexpected error: %s reader was trying to parse: http://www.inspectionsonline.us%s")%(sys.exc_info()[0] ,  line) )
			if data != None:
				bizinfo={}
				biztable=driver.find_element_by_css_selector('table').find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')
				bizinfo['FacName']=biztable[0].text.strip()
				bizinfo['Address']=biztable[2].text.split('Address:')[1].strip()
				bizinfo['FacType']=biztable[3].text.split('Type:')[1].strip()
				bizinfo['Phone']=biztable[4].text.split('Telephone:')[1].strip()
				recordrow = soup.find('table',{'id':'vwTbl'}).findAll('tr')
				logging.debug(('recordrow set %s')%(recordrow))
				for row in recordrow:
					logging.debug(('current row is %s')%(row))
					if row.find('th'):
						continue
					mylink=row.find('a').get('href')
					logging.debug(('mylink set to %s')%(mylink))
					if mylink:
						inspectid=(mylink.__str__().split('pUNID=')[1] )
						inspurl=('http://www.inspectionsonline.us%s')%(mylink)
						for trying in range (4):
							try:
								insppage=requests.get(inspurl)
								break
							except (ConnectionError, ConnectionResetError):
								logging.exception(("Connection error reader was trying to get: http://www.inspectionsonline.us%s and trying: %s")%(mylink, tries))
								time.sleep(3)
							except Exception:
								logging.exception(("Unexpected error: %s reader was trying to get: http://www.inspectionsonline.us%s")%(sys.exc_info()[0], mylink))
						try:
							inspsoup=BeautifulSoup(insppage.text,'html.parser')
							insptable=inspsoup.find('table').findAll('tr')
							inspectdata={}
							inspectdata['InspType']=insptable[9].findAll('td')[1].text.strip()
							inspectdata['InspDate']=insptable[8].findAll('td')[1].text.strip()
							inspectdata['InspCrit']=insptable[10].findAll('td')[1].text.strip()
							inspectdata['InspViolCount']=insptable[11].findAll('td')[1].text.strip()
							inspections[inspectid]=inspectdata
						except Exception:
							logging.exception(("Unexpected error: %s reader was trying to parse inspections: http://www.inspectionsonline.us%s")%(sys.exc_info()[0] ,  mylink) )
				#parse table cells in each row
				#save text, recordid in row
				#add all data for each row to list or dictionary
				logging.debug('inspections is: ' + str(inspections))
				c.execute('INSERT INTO jsonfac VALUES (?,?)', (bizid, json.dumps(bizinfo)))
				jsoninspect = []
				for inspection in inspections:
					jsoninspect.append((inspection, json.dumps(inspections[inspection])))
				c.executemany('INSERT INTO jsoninsp VALUES (?,?)', jsoninspect )
				conn.commit()
			else:
				logging.warning(("No data found: %s soup: %s")%(line, soup) )
	conn.close()
	driver.quit()





































