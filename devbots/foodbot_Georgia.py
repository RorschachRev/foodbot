import requests
import json
from bs4 import BeautifulSoup
import sys, time, os
import logging
import logging.handlers
import redis
import pickle

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_Georgia.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
#~ root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	#~ queryset=[30002,30003,30004,30005,30006,30007,30008,30009,30010,30011,30012,30013,30014,30015,30016,30017,30018,30019,30021,30022,30023,30024,30025,30026,30028,30029,30030,30031,30032,30033,30034,30035,30036,30037,30038,30039,30040,30041,30042,30043,30044,30045,30046,30047,30048,30049,30052,30054,30055,30056,30058,30060,30061,30062,30063,30064,30065,30066,30067,30068,30069,30070,30071,30072,30073,30074,30075,30076,30077,30078,30079,30080,30081,30082,30083,30084,30085,30086,30087,30088,30090,30091,30092,30093,30094,30095,30096,30097,30098,30099,30101,30102,30103,30104,30105,30106,30107,30108,30109,30110,30111,30112,30113,30114,30115,30116,30117,30118,30119,30120,30121,30122,30123,30124,30125,30126,30127,30129,30132,30133,30134,30135,30137,30138,30139,30140,30141,30142,30143,30144,30145,30146,30147,30148,30149,30150,30151,30152,30153,30154,30156,30157,30160,30161,30162,30163,30164,30165,30168,30169,30170,30171,30172,30173,30175,30176,30177,30178,30179,30180,30182,30183,30184,30185,30187,30188,30189,30204,30205,30206,30212,30213,30214,30215,30216,30217,30218,30219,30220,30222,30223,30224,30228,30229,30230,30233,30234,30236,30237,30238,30240,30241,30248,30250,30251,30252,30253,30256,30257,30258,30259,30260,30261,30263,30264,30265,30266,30268,30269,30270,30271,30272,30273,30274,30275,30276,30277,30281,30284,30285,30286,30287,30288,30289,30290,30291,30292,30293,30294,30295,30296,30297,30298,30301,30302,30303,30304,30305,30306,30307,30308,30309,30310,30311,30312,30313,30314,30315,30316,30317,30318,30319,30320,30321,30322,30324,30325,30326,30327,30328,30329,30330,30331,30332,30333,30334,30336,30337,30338,30339,30340,30341,30342,30343,30344,30345,30346,30347,30348,30349,30350,30353,30354,30355,30356,30357,30358,30359,30360,30361,30362,30363,30364,30366,30368,30369,30370,30371,30374,30375,30376,30377,30378,30379,30380,30384,30385,30386,30387,30388,30389,30390,30392,30394,30396,30398,30399,30401,30410,30411,30412,30413,30414,30415,30417,30420,30421,30423,30424,30425,30426,30427,30428,30429,30434,30436,30438,30439,30441,30442,30445,30446,30447,30448,30449,30450,30451,30452,30453,30454,30455,30456,30457,30458,30459,30460,30461,30464,30467,30470,30471,30473,30474,30475,30477,30499,30501,30502,30503,30504,30506,30507,30510,30511,30512,30513,30514,30515,30516,30517,30518,30519,30520,30521,30522,30523,30525,30527,30528,30529,30530,30531,30533,30534,30535,30536,30537,30538,30539,30540,30541,30542,30543,30544,30545,30546,30547,30548,30549,30552,30553,30554,30555,30557,30558,30559,30560,30562,30563,30564,30565,30566,30567,30568,30571,30572,30573,30575,30576,30577,30580,30581,30582,30596,30597,30598,30599,30601,30602,30603,30604,30605,30606,30607,30608,30609,30612,30619,30620,30621,30622,30623,30624,30625,30627,30628,30629,30630,30631,30633,30634,30635,30638,30639,30641,30642,30643,30645,30646,30647,30648,30650,30655,30656,30660,30662,30663,30664,30665,30666,30667,30668,30669,30671,30673,30677,30678,30680,30683,30701,30703,30705,30707,30708,30710,30711,30719,30720,30721,30722,30724,30725,30726,30728,30730,30731,30732,30733,30734,30735,30736,30738,30739,30740,30741,30742,30746,30747,30750,30751,30752,30753,30755,30756,30757,30802,30803,30805,30806,30807,30808,30809,30810,30811,30812,30813,30814,30815,30816,30817,30818,30819,30820,30821,30822,30823,30824,30828,30830,30833,30901,30903,30904,30905,30906,30907,30909,30911,30912,30913,30914,30916,30917,30919,30999,31001,31002,31003,31004,31005,31006,31007,31008,31009,31010,31011,31012,31013,31014,31015,31016,31017,31018,31019,31020,31021,31022,31023,31024,31025,31026,31027,31028,31029,31030,31031,31032,31033,31034,31035,31036,31037,31038,31039,31040,31041,31042,31044,31045,31046,31047,31049,31050,31051,31052,31054,31055,31057,31058,31059,31060,31061,31062,31063,31064,31065,31066,31067,31068,31069,31070,31071,31072,31075,31076,31077,31078,31079,31081,31082,31083,31084,31085,31086,31087,31088,31089,31090,31091,31092,31093,31094,31095,31096,31097,31098,31099,31106,31107,31119,31120,31126,31131,31136,31139,31141,31145,31146,31150,31156,31191,31192,31193,31195,31196,31197,31198,31199,31201,31202,31203,31204,31205,31206,31207,31208,31209,31210,31211,31212,31213,31216,31217,31220,31221,31294,31295,31296,31297,31301,31302,31303,31304,31305,31307,31308,31309,31310,31312,31313,31314,31315,31316,31318,31319,31320,31321,31322,31323,31324,31326,31327,31328,31329,31331,31333,31401,31402,31403,31404,31405,31406,31407,31408,31409,31410,31411,31412,31414,31415,31416,31418,31419,31420,31421,31501,31502,31503,31510,31512,31513,31515,31516,31518,31519,31520,31521,31522,31523,31524,31525,31527,31532,31533,31534,31535,31537,31539,31542,31543,31544,31545,31546,31547,31548,31549,31550,31551,31552,31553,31554,31555,31556,31557,31558,31560,31561,31562,31563,31564,31565,31566,31567,31568,31569,31598,31599,31601,31602,31603,31604,31605,31606,31620,31622,31623,31624,31625,31626,31627,31629,31630,31631,31632,31634,31635,31636,31637,31638,31639,31641,31642,31643,31645,31647,31648,31649,31650,31698,31699,31701,31702,31703,31704,31705,31706,31707,31708,31709,31710,31711,31712,31714,31716,31719,31720,31721,31722,31727,31730,31733,31735,31738,31739,31743,31744,31747,31749,31750,31753,31756,31757,31758,31760,31763,31764,31765,31768,31769,31771,31772,31773,31774,31775,31776,31778,31779,31780,31781,31782,31783,31784,31787,31788,31789,31790,31791,31792,31793,31794,31795,31796,31798,31799,31801,31803,31804,31805,31806,31807,31808,31810,31811,31812,31814,31815,31816,31820,31821,31822,31823,31824,31825,31826,31827,31829,31830,31831,31832,31833,31836,31901,31902,31903,31904,31905,31906,31907,31908,31909,31914,31917,31993,31995,31997,31998,31999,39813,39815,39817,39818,39819,39823,39824,39825,39826,39827,39828,39829,39832,39834,39836,39837,39840,39841,39842,39845,39846,39851,39852,39854,39859,39861,39862,39866,39867,39870,39877,39885,39886,39897,39901]
	queryset=[30002]
	f=[]
	resultnum=-1
	currentnum=0
	info=''
	for val in queryset:
		data=False
		pageurl=(('http://ga.healthinspections.us/gwinnett_new/search.cfm?start=%s1&F=s&S=%s&R=zip&MAJORTYPE=All&SEARCH=Search&GRADELETTER=All&')%(currentnum,val))
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
			soup=BeautifulSoup(page.text, 'html.parser')
			data=soup.findAll(valign="top")
			resultnum=int(int(data[1].find('b').getText().split(' ')[0])/10)
			if resultnum==-1:
				logging.info(" Search failed ")
		except Exception:
			logging.exception( ("Unexpected error: %s was trying to parse: %s") %( sys.exc_info()[0] ,  pageurl) )
		if resultnum!=-1:
			info=data[1].findAll('a')
			for value in range(0, info.__len__()-1-resultnum):
				url=info[value]['href']
				fappend(url.strip())
			while resultnum != currentnum:
				currentnum=currentnum+1
				pageurl=(('http://ga.healthinspections.us/gwinnett_new/search.cfm?start=%s1&F=s&S=%s&R=zip&MAJORTYPE=All&SEARCH=Search&GRADELETTER=All&')%(currentnum,val))
				for tries in range(4):
					try:
						page=requests.get(pageurl)
						logging.info(('got %s' )%(pageurl))
						time.sleep(1)
						break
					except (ConnectionError, ConnectionResetError):
						logging.exception(("Connection error was trying to get: %s and trying: %s")%(pageurl, tries))
						time.sleep(30)
					except Exception:
						logging.exception(("Unexpected error: %s was trying to get: %s")%(sys.exc_info()[0], pageurl))
				for tries in range(4):
					soup=BeautifulSoup(page.text, 'html.parser')
					if soup == "The service is unavailable.":
						time.sleep(30)
					else:
						break
				#~ logging.info(soup)
				data=soup.findAll(valign="top")
				#~ logging.info(data[1])
				info=data[1].findAll('a')
				for val in range(0, info.__len__()-1-resultnum):
					url=info[val]['href']
					f.append( url.strip())
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	donekeys=r.keys('canGA_*')
	logging.info(('donekeys has %s entries')%(donekeys.__len__()))
	print(("donekeys has %s entries") % (donekeys.__len__() ) )
	for line in f:
		bizid=str(line.split('=')[1]).strip()
		keyname=('canGA_%s')%(bizid)
		#~ todokeyname=('TODO_GA_%s')%(bizid)
		if  donekeys.__contains__(keyname.encode("utf-8")):
			#~ if not donetodo.__contains__(todokeyname.encode('utf-8')):
			continue
			#~ else
				#~ logging.info(('%s is already done, but had unfinished inspections')%(bizid))
		else:
			logging.info(('Getting data for %s')%(bizid))
		inspections={}
		data=None
		inspecturl=''
		inspectid=''
		line=line.strip()
		for tries in range(4):
			try:
				page=requests.get(('http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				logging.debug(('page got http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				time.sleep(1.5)
				break
			except (ConnectionError,ConnectionResetError):
				logging.exception(('Connection error reader was trying to get: http://ga.healthinspections.us/gwinnett_new/%s and trying %s')%(line,tries))
				time.sleep(3)
			except Exception:
				logging.exception(('Unexpected error: %s reader was trying to get: http://ga.healthinspections.us/gwinnett_new/%s')%(sys.exc_info[0],line))
		try:
			for tries in range(4):
				soup = BeautifulSoup(page.text, 'html.parser')
				if soup.text.__contains__("The service is unavailable."):
					logging.warning((' %s The service is unavailable')%(bizid))
					time.sleep(15)
					page=requests.get(('http://ga.healthinspections.us/gwinnett_new/%s')%(line))
				else:
					break
			data=soup.find(bgcolor='#FFFFFF').find('div').findAll('table')	#TODO?: redo as td class="body"	
			#TODO if no table, save "No inspections found" as a list element to REDIS
			logging.debug('table found ' + str(data))
			logging.debug(data.__len__())
			if data == None:
				logging.info(" Search failed ")
				inspections[status]="No inspections found"
		except Exception:
			logging.exception(("Unexpected error: %s reader was trying to parse: http://ga.healthinspections.us/gwinnett_new/%s")%(sys.exc_info()[0] ,  line) )
		if data!=None:
			for val in range(0,data.__len__(),2):
				inspectid=data[val].find('a').get('href').split("=")[1].split('&')[0]
				inspections[inspectid]={}
				a=data[val].find('a')
				inspecturl=a.get('href').strip('..')
				a=a.parent.find_next_sibling('td')
				inspectdate=a.getText().split(':')[1].strip()       
				a=a.find_next_sibling('td')
				inspections[inspectid]['InspUrl']=inspecturl
				inspections[inspectid]['InspDate']=inspectdate
				inspectgrade=a.getText().split(':')[1].strip()
				inspections[inspectid]['InspGrade']=inspectgrade
				if not inspectgrade:
					later={}
					later['bizurl']=('http://ga.healthinspections.us/gwinnett_new/%s')%(line)
					later['inspecturl']=('http://ga.healthinspections.us%s')%(inspecturl)
					r.set(("TODO_GA_%s")%(bizid), pickle.dumps(later))
				Viol=data[val].find_next_sibling('table').findAll(bgcolor="efefef")
				if Viol:
					inspections[inspectid]['Violtable']={}
					for val in range(0, Viol.__len__()):
						inspections[inspectid]['Violtable'][val]={}
						table=Viol[val].findAll('td')
						inspections[inspectid]['Violtable'][val]['InspViolcode']=table[0].getText().strip()
						inspections[inspectid]['Violtable'][val]['InspViolDesc']=table[1].getText().strip()
						inspections[inspectid]['Violtable'][val]['InspViolOccur']=table[2].getText().strip()
		#TODO: If no "Grade:" we need to digest the actual report?
		logging.debug(("Inspections: %s")%(inspections))
		if inspections:	#This is why it is not writing... but I want you to figure out why not.
			r.set(('canGA_%s')%(bizid), pickle.dumps(inspections))
		else:
			logging.warning(('No data found: %s soup: %s')%(line, soup))