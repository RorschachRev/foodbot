import requests
import json
import logging
import logging.handlers
import os, sys, time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_Id_bonneville.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
if __name__ == '__main__':
	queryset=['A*', "B*","C*", 'D*','E*','F*','G*','H*','I*','J*','K*','L*','M*','N*','O*','P*','Q*','R*','S*','T*','U*','V*','W*','X*','Y*','Z*']
	#~ queryset=['A*',]
	urls=[]
	f=open("raw_out.txt","w")
	for val in queryset:
		data=False
		pageurl=('http://www.inspectionsonline.us/MT/FlatheadKalispell/Inspect.nsf/SearchEstab?SearchView&Query=[fld_Program]+CONTAINS+kw_Food+AND+([fld_EstabName]+CONTAINS+%s+OR+[fld_FaciName]+CONTAINS+%s)&SearchOrder=4&SearchWV=TRUE&SearchFuzzy=FALSE')%(val,val)
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
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if data:
			for value in data:
				url=value['href']
				f.write( url.strip())
				f.write( "\n")
	f.close()
	














































