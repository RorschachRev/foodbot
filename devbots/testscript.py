import requests
import pickle
#~ import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup
import sqlite3
import json

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_AZ_Cochise.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	#~ queryset=[]		#skip the search run
	queryset=['85635']  #test queryset 177 items
	#~ queryset=['85602','85603','85605','85606','85607','85608','85609','85610','85613','85615','85616','85617','85620','85625','85626','85627','85630','85632','85635','85638','85643','85650']
	inspecturls=set()
	#~ cur= conn.cursor()
	pageurl="http://cochise.healthinspections.us/cochise/index.cfm?page=search"
	for val in queryset:
		url=''
		data={}
		for x in range(1,6000,12):
			pageurl=('http://cochise.healthinspections.us/cochise/index.cfm?page=search&result=%s') % (x)
			for tries in range(4):
				try:
					page= requests.post(pageurl, data = {'keyword': val, 'type_filter':'Food'})
					break
				except (ConnectionError, ConnectionResetError):
					logging.exception(("Connection error was trying to get: %s and trying: %s")%(val, tries))
					time.sleep(3)
				except Exception:
					logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], val))
			try:
				soup=BeautifulSoup(page.text,'html5lib')
				data=soup.find('div', {"class": 'facilitiesrow'} )
			except Exception:
				logging.exception( ("Unexpected error: %s was trying to soup: %s") %( sys.exc_info()[0] ,  val) )			
			#~ if not soup.find('input', {'value':"next >>"} ):		#this would have made sense
				#~ break
			try:
				a=data.findAll('a')
				print(len(a))
				if(len(a)) > 0:
					for value in a:
						href=value['href'].strip()[1:]	#remove the . in front
						url=('http://cochise.healthinspections.us%s')%(href)
						#~ facid=urllib.parse.parse_qs(url)['id']
						#~ inspecturls.append(url)	#list style
						inspecturls.add(url)			#set style
				if(len(a))< 12:									#this shit should work.
					break
			except Exception:
				logging.exception( ("Unexpected error: %s was trying to soup: %s") %( sys.exc_info()[0] ,  val) )			
			time.sleep(5)
			