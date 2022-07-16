import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_IL_ChampaignUrbana.log"))
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
	for permit in range(1, 3000): 
		data={}
		info={}
		inspections={}
		url=('http://restaurants.cu-citizenaccess.org/restaurants/api/overview/?format=json&rest_permit=%s')%(permit)
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
		if page.json()['meta']['total_count'] > 0:
			data=page.json()['objects'][0]
			for inspection in data['onlinereports']:
				date=inspection['insp_date']
				score=inspection['insp_score']
				inspections[date]=score
			info['zip']=data['rest_zip']
			info['history']=data['rest_history']
			info['city']=data['rest_city']
			info['address']=data['rest_address']
			info['name']=data['rest_name']
			info['median_score']=data['median_score']
			info['inspections']=inspections
		r.set(('IL_ChampaignUrbana_%s')%(permit), pickle.dumps(info))
