import requests
import pickle
import logging
import logging.handlers
import redis
import sys,os,time
from bs4 import BeautifulSoup

handler = logging.handlers.WatchedFileHandler(
    os.environ.get("LOGFILE", "food_IL_Fayette.log"))
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
	url='http://allencountyhealthinspector.acfw.net/searches/results' #_method=POST&data%5BSearch%5D%5Bname%5D=&data%5BSearch%5D%5Baddress%5D=+++