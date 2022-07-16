#!/usr/bin/python3
import requests
import pickle
import urllib
#~ import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import sqlite3
import json
from pprint import pprint

#canon = canonical identifiier for url
#utype= 0 is nothing
#	faclist is 1
#	fac is 2
#	insp is 3
#URL is actual url, with http
#datafield is the requests dictionary, "data"
#status  0 is not run, 1 is success, 2 is error
class buildFacList:
	def __init__(self, db):
		self.db=dbfile
		pass
	def build(self):
		"""Sets up the list of facility names to query by programmer inference from website, typically zipcode or alphabetical. 
		Saves results to database, urlbot table"""
		#Note: trying to not go crazy on function names. This is poor organization and will need refactoring, but runs easy for now.
		#~ queryset=[]		#skip the search run
		#~ queryset=['85635']  #test queryset 177 items
		queryset=['85602','85603','85605','85606','85607','85608','85609','85610','85613','85615','85616','85617','85620','85625','85626','85627','85630','85632','85635','85638','85643','85650']
		pageurl="http://cochise.healthinspections.us/cochise/index.cfm?page=search"
		for val in queryset:	
			data={}
			listurl=[]
			for x in range(1,1000,12):	#maximum 1000 records for a search result
			#~ for x in range(1,24,12):
				pageurl=('http://cochise.healthinspections.us/cochise/index.cfm?page=search&result=%s') % (x)
				datafield = {'keyword': val, 'type_filter':'Food'}
				#TODO add search types besides Food
				#todo add to set
				canon=str(val)+"_"+str(x)
				listurl.append( (canon, 1, pageurl, json.dumps(datafield), 0) )
				data[canon]=(1, pageurl, datafield, 0)
			#add data to db
			#~ pprint(listurl)
			self.db =  sqlite3.connect(dbfile)
			self.cur= self.db.cursor()
			self.cur.executemany('REPLACE INTO urlbot VALUES (?,?,?,?,?)', listurl )
			self.db.commit()
			self.db.close()
	

if True:	#setup logging
	handler = logging.handlers.WatchedFileHandler(
	    os.environ.get("LOGFILE", "../logs/food_AZ_Cochise.log"))
	formatter = logging.Formatter(logging.BASIC_FORMAT)
	handler.setFormatter(formatter)
	root = logging.getLogger()
	#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
	root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
	root.addHandler(handler)

if __name__ == '__main__':
	firstrun= True
	#~ firstrun= False
	refresh_fac=False
	dbfile='../db/db.az_cochise'
	conn = sqlite3.connect(dbfile)
	if firstrun:
		
		conn.execute("CREATE TABLE IF NOT EXISTS jsonfac(facid, json text)")
		conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsonfac_index ON jsonfac(facid)")
		conn.execute("CREATE TABLE IF NOT EXISTS jsoninsp(inspid text, json text)")
		conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS jsoninsp_index ON jsoninsp(inspid)")
		conn.execute("CREATE TABLE IF NOT EXISTS urlbot(canon text, utype int1, url text, datafield text, status int1)")
		conn.execute("CREATE INDEX IF NOT EXISTS urlbot_index ON urlbot(utype)")
		conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS urlbot_canon ON urlbot(canon, utype)")
		conn.commit()
		conn.close()
	### STEP ONE - Build URLS type 1 = fac ###
		run=buildFacList(dbfile)
		run.build()
	conn.close()
	### STEP TWO - Run bot on URLS type 1 = fac ###	
	conn = sqlite3.connect(dbfile)
	c=conn.cursor()
	for r in c.execute("SELECT * FROM urlbot WHERE utype=2 AND status=0"):
		row=[r[0],r[1],r[2],r[3],r[4]]
		page=None
#~ >>> url="http://cochise.healthinspections.us/index.cfm?page=facility&id=2479&type=Food"
#~ >>> soup=BeautifulSoup(requests.get(url).text,'html5lib')
		for tries in range(4):
			try:
				page= requests.post(row[2], data = json.loads(row[3]) )
				if page.status_code is 200:
					break
			except (ConnectionError, ConnectionResetError):
				logging.exception(("Connection error was trying to get: %s and trying: %s")%(val, tries))
				time.sleep(3)
			except Exception:
				logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], row[2]))
		if page:
			try:
				soup=BeautifulSoup(page.text,'html5lib')
				data=soup.find('div', {"class": 'facilitiesrow'} )
				if data:
					a=data.findAll('a')
					#TODO determine between error message on page and end of data
					#TODO flag all subsequent zipcode searches as complete if reached end of data
					#~ logging.info(len(a), len(inspecturls) )
					if(len(a)) > 0:
						for value in a:
							href=value['href'].strip()[1:]	#remove the . in front
							url=('http://cochise.healthinspections.us%s')%(href)
							facid=urllib.parse.parse_qs(url)['id']
							if type(facid) is type([]):
								facid=facid[0]
							if type(facid) is type([]):
								facid=facid[0]
							#~ inspecturls.append(url)	#list style
							#~ inspecturls.add(url)			#set style
							cur=conn.cursor()
							cur.execute("REPLACE INTO urlbot VALUES (?,?,?,?,?)", ( facid, 2, url, '{}', int(0) ) ) 	#id, facility URL, actual URL, no data parameter, not run
							conn.commit()
						row[4]= 1 #set as success
						cur=conn.cursor()
						cur.execute("REPLACE INTO urlbot VALUES (?,?,?,?,?)", row ) 
						conn.commit()
					else:
						logging.exception( ("No entries found on: %s for page \n %s") %( row[2], page.text) )
						break					
					#~ if(len(a))< 12:									#this shit should work.
						#~ logging.exception( ("No entries found on: %s for page \n %s") %( row[0], page) )
						#~ break
				else:	#no data found
					h3=soup.find("h3")
					if h3:
						if h3.text is "Page Temporarily Unavailable - cochise.healthinspections.us":
							print("Overloaded their server. Again.")
							break
					row[4]= 2 #set as error
					cur=conn.cursor()
					cur.execute("REPLACE INTO urlbot VALUES (?,?,?,?,?)", row ) 
					conn.commit()
			except Exception:
				logging.exception( ("Unexpected error: %s was trying to parse url from: %s") %( sys.exc_info()[0] ,  row[2]) )
			time.sleep(2) 		#IIS Sucks.	
			#~ logging.info(('Found a cumulative total of %s facilities by end of %s') % (len(inspecturls), val) )
	conn.close()

	#~ cur.execute("select * from jsonfac WHERE facid=:id", {"id":data['FacID']})
	
	### STEP THREE - Run bot on list of facility URL and save facility details to jsoninsp DB	###
	#~ inspecturls=['http://cochise.healthinspections.us/cochise/index.cfm?page=facility&id=419&type=Food']	#test data, single result	
	#~ for line in inspecturls:
	conn = sqlite3.connect(dbfile)
	c=conn.cursor()
	cur=conn.cursor()
	for r in c.execute("SELECT * FROM urlbot WHERE utype=2 AND status=0"):
		line=r[2]	#actual URL, which is used repeatedly
		row=[r[0],r[1],r[2],r[3],r[4]]
		data={}
		details=[]
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
			soup=BeautifulSoup(page.text,'html5lib')
			data['FacID']=line.split("=")[2].split('&')[0]
			h3=soup.find("h3")
			if h3:
				if h3.text is "Page Temporarily Unavailable - cochise.healthinspections.us":
					print("Overloaded their server. Again.")
					break
			cur.execute("select * from jsonfac WHERE facid=:id", {"id":data['FacID']})
			get_one=cur.fetchone()  #named after redis "get"
			if get_one is None:  #suspend and resume - if we have no data, then get it!	for val in queryset:
				jsoninspect=[]
				findfac= soup.find("div",{'class':'fac_and_insp'})
				if findfac:
					details=findfac.findAll('h5')				
					#~ pprint(details)
					
					data['Name'] =		details[0].text.split(':')[1].strip()
					data['FacType']=	details[1].text.split(':')[1].strip()
					data['Address']=	details[2].text.split(':')[1].strip()
					data['FacURL']=line
					facdata=json.dumps(data)
					cur= conn.cursor()
					cur.execute("REPLACE INTO jsonfac VALUES (?,?)", (data['FacID'], facdata)) #insert description into jsonfac
					conn.commit()
		### STEP FOUR: Save URL for inspections ###
			#note, this site has "most" of the details on the facilities page, and I'm saving them from here into the facility
		### STEP FIVE: load inspections 			
					for i in soup.findAll("div",{'class':'inspection_bar'}):
						ins=i.findAll('div')
						inspec={}
						try:
							inspec['Type']=ins[1].text.strip()+", "+ins[2].text.strip()
							x=i.find('a')['href'][11:]
							inspec['Link']=('http://cochise.healthinspections.us%s') % (x)
							#~ http://cochise.healthinspections.us/_templates/623/Food%20Inspection/_report_full.cfm?inspectionID=96391&parentTableName=tblInspection&dsn=DHD_623&domainid=623
							#TODO: save this to urlbot for saving individual inspections
							inspec['ID']= i['id']
							inspec['Date']=ins[0].text.strip()
							inspec['Summary']=ins[3].text.strip()
							jsoninspect.append((inspec['ID'], json.dumps(inspec))) #Add items
						except Exception:
							logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )

					cur=conn.cursor()
					row[4]= 1 #set as success
					cur.executemany('REPLACE INTO jsoninsp VALUES (?,?)', ( jsoninspect))
					cur.execute("REPLACE INTO urlbot VALUES (?,?,?,?,?)", row ) 
					conn.commit()
					
				else:
					h3=soup.find("h3")
					if h3:
						if h3.text is "Page Temporarily Unavailable - cochise.healthinspections.us":
							print("Overloaded their server. Again.")
							break
					else:
						print( ("Error finding content on %s") % (line) )
						pprint(findfac)
						pprint(details)
						pprint(soup.text)
					
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )		
		time.sleep(2)				
	conn.close()
#TODO: save as PDF
#http://cochise.healthinspections.us/_templates/623/Food%20Inspection/_report_full.cfm?inspectionID=96391&parentTableName=tblInspection&dsn=DHD_623&domainid=623
