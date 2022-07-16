from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

profile=webdriver.FirefoxProfile('nfapbgy1.Metamask') #have to copy file to current directory
driver=webdriver.Firefox(profile)
#abcd1234
#broken buyer bubble axis hard carbon little rhythm phrase saddle thrive siege
#0xc301504BEb55bd7672dA21D542cFdDE8F9D4DE46
for tries in range(4):
	try:
		driver.get('moz-extension://14c6d9a2-b501-4484-808f-227ccdd5e85c/home.html')
		password=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
		password=driver.find_element_by_id('password')
		password.clear()
		password.send_keys('abcd1234')
		password.submit()
		break
	except Exception:
		print(Exception)
#find how to save profile (I think it automatically does that if not using default)
#how to load profile
#make 3 profiles
#install metamask with account above into one profile.


#selenium as unit testing
#read contents of page

url='https://sqa.stackexchange.com/questions/2197/how-to-download-a-file-using-seleniums-webdriver'
driver.get(url)
cookies=driver.get_cookies() #read all the cookies, save the output
print(cookies)

#read some javascript variables from page, save the output

for cookie in cookies: #load cookie from saved output
	driver.add_cookie(cookie) #This will only work if you are currently at the domain of the cookies you want to set


#load javascript, assign JS variable from saved output.

#change timing to server ready / page loaded fully  event based instead of sleep