import pickle
import redis
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

if __name__ == '__main__':
	r=redis.StrictRedis(host='localhost',port=6379,db=0)
	profile=webdriver.FirefoxProfile("jno3ab90.foodbot")
	#~ profile.getProfile("foodbot");
	profile.set_preference("browser.download.folderList", 2)
	#~ profile.set_preference('browser.download.dir', './downloads/')
	profile.set_preference('browser.download.dir', '/home/lewis/foodbot.sorry/downloads/')
	profile.set_preference('browser.download.manager.showWhenStarting',False)
	profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/pdf,application/octet-stream')
	driver=webdriver.Firefox(profile)
	url='http://health.grantcounty27.us/cgi.exe?CALL_PROGRAM=REPORTS'
	driver.get(url)
	driver.implicitly_wait(2)
	maxperpage=driver.find_element_by_name('SYS_MAXPERPAGE')
	maxperpage.clear()
	maxperpage.send_keys('1000')
	maxperpage.submit()
	time.sleep(2)
	evenrows=driver.find_elements_by_class_name('evenrow')
	evenlen=evenrows.__len__()
	for row in range(evenlen):
		name=evenrows[row-1].find_element_by_css_selector('a').text
		rowurl=evenrows[row-1].find_element_by_css_selector('a').get_attribute('href').split('=')
		keyname=name+rowurl[rowurl.__len__()-1].strip()
		if r.keys(('foodSe_IN_Grant_%s')%(keyname)):
			continue
		evenrows[row-1].find_element_by_css_selector('a').click()
		element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "download")))
		driver.find_element_by_id('download').click()
		r.set(('foodSe_IN_Grant_%s')%(keyname),'Might exist in downloads')
		driver.back()
		time.sleep(2)
		evenrows=driver.find_elements_by_class_name('evenrow')
	oddrows=driver.find_elements_by_class_name('oddrow')
	oddlen=oddrows.__len__()
	for row in range(oddlen):
		name=oddrows[row-1].find_element_by_css_selector('a').text
		rowurl=oddrows[row-1].find_element_by_css_selector('a').get_attribute('href').split('=')
		keyname=name+rowurl[rowurl.__len__()-1].strip()
		if r.keys(('foodSe_IN_Grant_%s')%(keyname)):
			continue
		oddrows[row-1].find_element_by_css_selector('a').click()
		element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "download")))
		driver.find_element_by_id('download').click()
		r.set(('foodSe_IN_Grant_%s')%(keyname),'Might exist in downloads')
		driver.back()
		time.sleep(2)
		oddrows=driver.find_elements_by_class_name('evenrow')
	for times in range(3): #up to 1000 results per page, this lets it continue to next pages
		driver.find_element_by_name('NEXT').click()
		time.sleep(2)
		evenrows=driver.find_elements_by_class_name('evenrow')
		evenlen=evenrows.__len__()
		for row in range(evenlen):
			name=evenrows[row-1].find_element_by_css_selector('a').text
			rowurl=evenrows[row-1].find_element_by_css_selector('a').get_attribute('href').split('=')
			keyname=name+rowurl[rowurl.__len__()-1].strip()
			if r.keys(('foodSe_IN_Grant_%s')%(keyname)):
				continue
			evenrows[row-1].find_element_by_css_selector('a').click()
			element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "download")))s
			driver.find_element_by_id('download').click()
			r.set(('foodSe_IN_Grant_%s')%(keyname),'Might exist in downloads')
			driver.back()
			time.sleep(2)
			evenrows=driver.find_elements_by_class_name('evenrow')
		oddrows=driver.find_elements_by_class_name('oddrow')
		oddlen=oddrows.__len__()
		for row in range(oddlen):
			name=oddrows[row-1].find_element_by_css_selector('a').text
			rowurl=oddrows[row-1].find_element_by_css_selector('a').get_attribute('href').split('=')
			keyname=name+rowurl[rowurl.__len__()-1].strip()
			if r.keys(('foodSe_IN_Grant_%s')%(keyname)):
				continue
			oddrows[row-1].find_element_by_css_selector('a').click()
			element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "download")))
			driver.find_element_by_id('download').click()
			r.set(('foodSe_IN_Grant_%s')%(keyname),'Might exist in downloads')
			driver.back()
			time.sleep(2)
			oddrows=driver.find_elements_by_class_name('oddrow')
	#~ driver.quit()