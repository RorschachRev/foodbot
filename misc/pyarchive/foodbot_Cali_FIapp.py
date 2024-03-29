#!/usr/bin/env python3
import requests
import json
import redis
import pickle
import logging
import logging.handlers
import os, sys, time

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_Cail.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)
 
#Seach by Zipcode for licenseIDs?
#For each result, fetch license info
#Parse and store all data from license result
#use BS.json to get python objects
if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	f=open('fullcalidump')
	j=json.load(f)
	#~ queryset=j	#Do this, or create a subjob by filter
	queryset=[]
	myagencylist=[ 616, 446, 582, 276, 106, 208, 684, 480]
	for line in j:	#done: [208, 4, 2]
		if(line['AgencyID'] in myagencylist ):	#Lewis has [2, 4, 514, 599, 531, 548, 463, 565 ] omen has [ 616, 446, 582, 276, 106, 208, 684, 480] server has [701, 497, 429]
			#unclaimed: 	[  633, 650]
			queryset.append(line)
	
	#~ for Lat in ['-33.86881']:
	#Determine keys in REDIS that match some sort of scope of work
	donekeys=r.keys("ca_*")
	logging.debug(("donekeys has %s entries") % (donekeys.__len__() ) )
	logging.debug(("queryset has %s entries") % (queryset.__len__() ) )
	print(("donekeys has %s entries") % (donekeys.__len__() ) )
	print(("queryset has %s entries") % (queryset.__len__() ) )
	
	for biz_data in queryset:
		keyname=("ca_%s_%s") % (biz_data['AgencyID'], biz_data['FacilityID'])
		if donekeys.__contains__(keyname.encode('utf-8')):
			continue
		#~ all=False
		#~ url='https://hsdmobile.cchealth.org/WSFFISMobile/facade/FindFacilitiesNearby/' + Lat + '/151.209290/300'
		
		#~ try:
			#~ page=requests.get(url)
		#~ except Exception:
			#~ logging.exception("Unexpected error: "+ sys.exc_info()[0] + " was trying to get: " + url)
		#~ try:
			#~ all=page.json()
		#~ except Exception:
			#~ logging.exception("Unexpected error: "+ sys.exc_info()[0] + " was trying to parse: " + url)
		#~ if all:
			#~ for biz_data in all:
		license=[]
		inspecturl='https://hsdmobile.cchealth.org/WSFFISMobile/facade/GetFacilityInspections/' + str(biz_data['AgencyID'] )+ '/' + str(biz_data['FacilityID']) + '/0.000000/0.000000'
		for tries in range(4):			
			try:
				inspectpage=requests.get(inspecturl)
				break
			except (ConnectionError, ConnectionResetError) :
				logging.exception("Connection error was trying to get: " + inspecturl + " and trying: "+ str(tries) )
				time.sleep(3)
			except Exception:
				logging.exception("Unexpected error: "+ str(sys.exc_info()[0]) + " was trying to get: " + inspecturl)
				break
		try:
			inspections=inspectpage.json()
		#~ if (biz_data['FacilityID'] == 'PR0020778'):
			#~ logging.info("Checking test data PR0020778")
			#~ testjsonPR0020778=json.loads("""{"Events":[{"ActionDescription":"","ActivityDate":"04\/05\/2016","Details":[],"FacilityDescription":null,"Grade":null,"Score":"","ServiceDescription":"Inspection"},{"ActionDescription":"","ActivityDate":"09\/11\/2015","Details":[],"FacilityDescription":null,"Grade":null,"Score":"","ServiceDescription":"Inspection"},{"ActionDescription":"","ActivityDate":"03\/03\/2015","Details":[{"Description":"Proper hot and cold holding temperatures, Major","InspectionRptURL":null,"ProgramCategory":"~","Summary":"","ViolationCode":"18"},{"Description":"Food stored at least 6 inches above floor, Minor","InspectionRptURL":null,"ProgramCategory":"~","Summary":"","ViolationCode":"51"},{"Description":"Proper warewashing and sanitizing procedures, Minor","InspectionRptURL":null,"ProgramCategory":"~","Summary":"","ViolationCode":"60"}],"FacilityDescription":null,"Grade":null,"Score":"","ServiceDescription":"Inspection"}],"Facility":{"Address1":"122 American Alley Ste B","AgencyID":463,"City":"Petaluma","FacilityID":"PR0020778","FacilityName":"2 London Foodies","Grade":"","HasFullInspectionReports":false,"Latitude":38.2343423653,"Longitude":-122.6409100784,"MilesDistant":0,"Phone":"(707) 774-6996","Score":"","State":"CA","ZIP":"94952"}}""")
			#~ if (inspections != testjsonPR0020778 ):
				#~ logging.info("failed to match data")
				#~ logging.info(inspections)
				#~ logging.info(testjsonPR0020778)
					
			license.append(biz_data)
			license.append(inspections)
			#~ if(biz_data['HasFullInspectionReports']):
				#~ print(str(biz_data['AgencyID']) + '_'+ str(biz_data['FacilityID']) + ' has full reports')
				#~ logging.info(str(biz_data['AgencyID']) + '_'+ str(biz_data['FacilityID']) + ' has full reports')
			r.set("ca_" + str(biz_data['AgencyID']) + '_'+ str(biz_data['FacilityID'] ) , pickle.dumps(license))
			logging.info("ca_" + str(biz_data['AgencyID']) + '_'+ str(biz_data['FacilityID']) + ' set')
		
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  inspecturl) )
		

