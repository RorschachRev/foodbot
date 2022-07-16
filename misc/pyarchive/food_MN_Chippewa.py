import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_MN_Chippewa.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
#~ root.setLevel(os.environ.get("LOGLEVEL", "DEBUG")) #10
root.setLevel(os.environ.get("LOGLEVEL", "INFO")) #20
#~ root.setLevel(os.environ.get("LOGLEVEL", "WARNING")) #30
#~ root.setLevel(os.environ.get("LOGLEVEL", "ERROR")) #40
root.addHandler(handler)

if __name__ == '__main__':
	r = redis.StrictRedis(host='localhost', port=6379, db=0)
	#~ form data for A view%3A_id1%3A_id201%3AsingleFacNameEB1=&%24%24viewid=!4uvo0o6gt8m0afpfzud5uppyx!&%24%24xspsubmitid=view%3A_id1%3A_id247%3A_id248%3AfirstLetterRepeat1%3A1%3A_id251&%24%24xspexecid=&%24%24xspsubmitvalue=&%24%24xspsubmitscroll=0%7C0&view%3A_id1=view%3A_id1
	#~ the main pages don't have urls to records