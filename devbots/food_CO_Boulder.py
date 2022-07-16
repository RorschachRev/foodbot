# uncompyle6 version 3.2.5
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.6.7 (default, Oct 22 2018, 11:32:17)
# [GCC 8.2.0]
# Embedded file name: /home/david/Dev/foodbot/bot_canon/food_CO_Boulder.py
# Compiled at: 2019-03-05 15:53:30
import requests, pickle, redis, logging, logging.handlers, os, sys, time
from bs4 import BeautifulSoup
import html5lib
from pprint import pprint
print('Imports Done...')

import time
ts = time.gmtime()
stamp = time.strftime("%Y-%m-%d %H:%M:%S", ts)

#Fix SSL Error Temporarily---------------
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
#----------------------------------------

handler = logging.handlers.WatchedFileHandler(os.environ.get('LOGFILE', '../logs/food_CO_Boulder.log'))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get('LOGLEVEL', 'INFO'))
root.addHandler(handler)
if __name__ == '__main__':
	queryset = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

	inspecturls = set()

	for val in queryset:
		pageurl = 'http://www.decadeonline.com/results.phtml?agency=bou&coding=BCPH_RATING&violsortfield=TB_CORE_INSPECTION_VIOL.UPDATE_BY&forceresults=1&offset=0&businessstreet=&city=&zip=&facilityid=&FTS=&soundslike=&sort=FACILITY_NAME&businessname=%s' % val
		for tries in range(4):
			try:
				page = requests.get(pageurl)
				break
			except (ConnectionError, ConnectionResetError, requests.exceptions.SSLError):
				logging.exception('%s' 'Exception1, Connection error was trying to get: %s and trying: %s' % (stamp, pageurl, tries))
				print("Exception1")
				time.sleep(3)
			except Exception:
				logging.exception('%s' 'Exception2, Unexpected error: %s was trying to get: %s' % (stamp, sys.exc_info()[0], pageurl))
				print("Exception2")
		try:
			soup = BeautifulSoup(page.text, 'html.parser')
			tableoflinks = soup.findAll('table')[0]
		except Exception:
			logging.exception('%s' 'Exception3, Unexpected error: %s was trying to parse: %s' % (stamp, sys.exc_info()[0], pageurl))
			print("Exception3")
		else:
			if tableoflinks:
				a = soup.findAll('a')
				for value in a:
					href = value['href'].strip()
					url = 'https://decadeonline.com/%s' % href
					inspecturls.add(url)

	print('Inspecturls set with', len(inspecturls), 'facilities to check.')
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	for line in inspecturls:
		data = {}
		inspections = []
		inspection = []
		print('1st for-loop variables set and initialized...')
		for tries in range(4):
			try:
				page = requests.get(line)
				logging.debug(line)
				break
			except (ConnectionError, ConnectionResetError, requests.exceptions.SSLError):
				logging.exception('Exception4, Connection error reader was trying to get: %s and trying: %s' % (line, tries))
				print('exception4')
				time.sleep(3)
			except Exception:
				logging.exception('Exception5, Unexpected error: %s reader was trying to get: %s' % (
				sys.exc_info()[0], line))
				print('exception5')

		try:
			somesearch = 'http://www.decadeonline.com/results.phtml?agency=bou&coding=BCPH_RATING&violsortfield=TB_CORE_INSPECTION_VIOL.UPDATE_BY&forceresults=1&offset=0&businessstreet=&city=&zip=&facilityid=&FTS=&soundslike=&sort=FACILITY_NAME&businessname=a'
			page = requests.get(somesearch)
			print('somesearch and page are set...')
			soup = BeautifulSoup(page.text, 'html5lib')
			tables = soup.findAll('table')
			details = tables[0].findAll('td')
			data['FacID'] = line.split('=')[1]
			if r.get('canCO_Boulder_fac_%s' % data['FacID']):
				print('Data exists:', data['FacID'])
			num = inspecturls.__len__()
			for x in range (num):
				data['Name'] = details[x].getText().strip()
				data['Address'] = details[x].getText().strip()
				for item in soup:
					s = tables[0].find('script').getText().strip()
					pacechar = s.find('pace')
					if s[pacechar:pacechar + 15].strip()[-3:-2] == 'Y':
						pacestatus = True
					else:
						pacestatus = False
						safechar = s.find('safe')
					if s[safechar:safechar + 15].strip()[-3:-2] == 'Y':
						safestatus = True
					else:
						safestatus = False
						data['Details'] = {'pace': pacestatus, 'safe': safestatus}
			print("soup digestion of list done...")
		except Exception:
			logging.exception('%s' 'Exception6, Unexpected error: %s reader was trying to parse: %s' % (stamp, sys.exc_info()[0], line))
			print('exception6')




		for val in range(0, inspections.__len__(), 2):
			try:
				inspec = {}
				inspection = inspections[val].findAll('td') + inspections[val + 1].findAll('td')
				inspec['Type'] = my_td[0].getText().strip()
				inspec['Link'] = 'fac.phtml?agency=BOU&amp;coding=BCPH_RATING&amp;violsortfield=TB_CORE_INSPECTION_VIOL.UPDATE_BY&amp;forceresults=1&amp;facid=%s' % x
				inspec['ID'] = x.split('=')[1]
				inspec['Date'] = my_td[1].getText().strip()
				inspec['Summary'] = my_td[2].getText().strip()
				inspections.append(inspec)
			except:
				logging.exception('%s' 'Exception7, Unexpected error: %s reader was trying to parse inspection: %s' % (stamp, sys.exc_info()[0], val))
				print('exception7')
			else:
				data['Inspections'] = inspections

		'''print (data['Name'], '\n', data['Address'], '\n', data['Details'])'''
	print (data['Name'], '\n', data['Address'])
	print('End of Script')
