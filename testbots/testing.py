import requests
import html5lib
from bs4 import BeautifulSoup

#Url and Soup Setup:
url = ('http://www.decadeonline.com/insp.phtml?agency=CAS&violsortfield=TB_CORE_INSPECTION_VIOL.VIOLATION_CODE&record_id=PR0000002')
page=requests.get(url)

soup=BeautifulSoup(page.text,'html5lib')
table=soup.findAll('table')

#Search Variables Setup:
#data1 = table[4].findAll('strong')
data2 = table[4].findAll('td')
#data3 = data2[2].findAll('span')[0].getText().strip()
#x = soup.findAll('td')

#Finished & Trimmed Variables
#titles = data1[0].getText().strip()#may not use this one...
date = data2[0].getText().strip()[0:10]# Or this one
details = data2[0].getText().strip()
entry = data2[2].findAll('span')[0].getText().strip()


#print(details)
#print(entry)
#-----------------------------------------------------
inspection={}
report={}

for x in range(len(table)):
    #TODO: Fill inspection with report(dict), add inspection type and date
    details = table[x+4].findAll('td')
    for y in range(len(data2), 2):
        #TODO: Increment details by two starting at two
        #fill report(dict) with inspection data from the site
        report['entry_title' + str(count)] = details
        report['entry_text' + str(count)] = entry
        print(entry)
        count += 1
    print(report)
    print('Report Finished...')
    print('--------------------------------------------------------------------')
    inspection['Date'] = entry
inspection['Inspections'] = report
print(inspection)
#-----------------------------------------------------