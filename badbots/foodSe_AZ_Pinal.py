#TODO 
#~ Having trouble pulling records because records are display by javascript:__doPostBack('ctl00$m$g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4$ctl00$ctl04$gv_Results$ctl02$lblTooltip',''))
import time
import pickle
import redis
import logging
import logging.handlers
import os, sys, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "../logs/food_AZ_Pinal.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR"))
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	driver=webdriver.Firefox()
	url='http://www.pinalcountyaz.gov/EnvironmentalHealth/Pages/Pinal-County-Food-Inspections.aspx'
	driver.get(url)
	driver.implicitly_wait(5)
	dropdown=driver.find_element_by_id('ctl00_m_g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4_ctl00_ctl02_ddl_City')
	dropdownselect=Select(dropdown)
	for val in range(dropdownselect.options.__len__()):
		dropdownselect.select_by_index(val)
		driver.find_element_by_id('ctl00_m_g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4_ctl00_ctl02_btn_City').click()
		#~ driver.find_elements_by_class_name('Acc_Header')[1].click()
		table=driver.find_element_by_css_selector('table#ctl00_m_g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4_ctl00_ctl04_gv_Results')
		results=table.find_elements_by_css_selector('tr')
		if table.find_element_by_class_name('Grd_pager'):
			pager=table.find_element_by_class_name('Grd_pager')
			pages=pager.find_elements_by_css_selector('td') #first element is not a page link
			for resultpage in range(1, pages.__len__()):
				for val in range(1,results.__len__()):
					data={}
					info=results[val].find_elements_by_css_selector('td')
					if r.keys(('food_AZ_Pinal_%s')%(info[1].text.strip())):
						continue
					data['FacName']=info[0].text.strip()
					data['InspDate']=info[1].text.strip()
					data['ScoreHI']=info[2].text.strip()
					data['Address']=info[3].text.strip()
					data['City']=info[4].text.strip()
					r.set(('food_AZ_Pinal_%s')%(info[1].text.strip()),pickle.dumps(data))
				try:
					t=pages[pagenum].find_element_by_css_selector('a')
				except NoSuchElementException:
					if pagenum + 1 == pages.__len__():
						break
					pages[pagenum + 1].click()
			#~ for pagenum in range(1,pages.__len__()):
				#~ try:
					#~ t=pages[pagenum].find_element_by_css_selector('a')
				#~ except NoSuchElementException:
					#~ if pagenum + 1 == pages.__len__():
						#~ break
					#~ pages[pagenum + 1].click()
					#~ break
			table=driver.find_element_by_css_selector('table#ctl00_m_g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4_ctl00_ctl04_gv_Results')
			results=table.find_elements_by_css_selector('tr')
		else:	
			for element in results:
				data={}
				info=element.find_elements_by_css_selector('td')
				if r.keys(('food_AZ_Pinal_%s')%(info[1].text.strip())):
					continue
				data['FacName']=info[0].text.strip()
				data['InspDate']=info[1].text.strip()
				data['ScoreHI']=info[2].text.strip()
				data['Address']=info[3].text.strip()
				data['City']=info[4].text.strip()
				r.set(('food_AZ_Pinal_%s')%(info[1].text.strip()),pickle.dumps(data))
		driver.find_elements_by_class_name('Acc_Header')[0].click()
		dropdown=driver.find_element_by_id('ctl00_m_g_241dedc4_0ae6_4e4e_9e19_ac4e291b82a4_ctl00_ctl02_ddl_City')
		dropdownselect=Select(dropdown)