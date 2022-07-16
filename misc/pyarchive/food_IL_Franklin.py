import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_IL_Franklin.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	#~ queryset=['1'] #test queryset
	queryset=['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
	f=open("raw_out.txt","w")
	for val in queryset:
		url=''
		data=False
		pageurl=('https://www.healthspace.com/Clients/Ohio/Franklin/Franklin_Web_Live.nsf/Food-List-ByFirstLetterInName?OpenView&Count=35&RestrictToCategory=%s')%(val)
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
			soup=BeautifulSoup(page.text,'html.parser')
			data=soup.findAll('table')[1]
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			a=data.findAll('a')
			for value in a:
				href=value['href']
				url=('https://www.healthspace.com%s')%(href)
				f.write(url.strip())
				f.write("\n")
	f.close()