#TODO 
#~ Having trouble pulling records because records are display in a document format
import requests
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_AZ_Yuma.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	#~ queryset=['37164']  #test queryset
	queryset=['37164','37622','39196','39633','28990','29519','31988','33501','26449','27144','27700','28474','23535','24091','24361','24903','20931','21549','22233','23003']
	inspecturls=[]
	for val in queryset:
		url=''
		data=False
		pageurl=('https://www.yumacountyaz.gov/home/showdocument?id=%s')%(val)
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
			soup=BeautifulSoup(page.text,'html5lib')
			#~ data=soup.findAll('table')[1]
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			a=data.findAll('a')
			for value in a:
			#~ for value in data:
				href=value['href'].strip()
				url=('https://www.yumacountyaz.gov%s')%(href)
				inspecturls.append(url)
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	#~ line ='https://www.yumacountyaz.gov/home/showdocument?id=37164'
	for line in inspecturls:
		data={}
		inspections=[]
		inspection=[]
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
			if(r.get( ('canAZ_Yuma_fac_%s')%(data['FacID']) )):
				print("Data exists:", data['FacID'])
				continue
			data['Name']=soup.find('h4').text
			detail = soup.findAll('h5')
			data['Address']=detail[3].text.split(':')[1].strip()
			data['FacType']=detail[2].text.split(':')[1].strip()
			data['FacURL']=line
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: %s")%(sys.exc_info()[0] ,  line) )				
		for val in range(0, inspection.__len__(), 3):	#3 td elements per tr, but no </tr>
			try:
				inspec={}
				inspec['Type']=inspection[val].getText().strip()
				#x was named sublink, but I don't want anyone to think it is stored or used.
				x=inspection[val].find('a')['href']
				inspec['Link']=('http://cochise.healthinspections.us/cochise/index.cfm?/%s') % (x)
				inspec['ID']= x.split("=")[1]
				inspec['Date']=inspection[val+1].getText().strip()
				inspec['Summary']=inspection[val+2].getText().strip()
				inspections.append(inspec)
			except:	
				#~ print(inspection[val])
				logging.exception(("Unexpected error: %s reader was trying to parse inspection: %s") % (sys.exc_info()[0] , val ) )
		data['Inspections']=inspections
		r.set(('canAZ_Yuma_fac_%s')%(data['FacID']), pickle.dumps(data))