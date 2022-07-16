import redis
import pickle

r = redis.StrictRedis(host='localhost', port=6379, db=0)
keys=r.keys('ca_*')
citys={}
for key in keys: #this for loop makes a key in all lowercase with the name of the city for each city
	city=pickle.loads(r.get(key))[0]['City']
	try:
		test=citys[city.lower()]
	except KeyError:
		citys[city.lower()]='ok'
compare=['el cajon'] #replace with the citys you want to find
for name in compare:
	if citys[name.lower()]:
		print(('a facility in %s has a record here')%(name))