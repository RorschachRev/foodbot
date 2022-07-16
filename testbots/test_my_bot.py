import argparse
import json
import pickle
import os
import sqlite3
import sys
import unittest

class TestBot(unittest.TestCase):
	
	ROW = ''

	def test_structure(self):
		data = self.ROW
		self.assertTrue(isinstance(data[0], int))
		self.assertTrue(isinstance(json.loads(data[1]), str))
	
	def test_facility(self):
		data = json.loads(self.ROW[2])
		self.assertTrue(data['Address'])
		self.assertTrue(data['Inspections'])

	def test_inspections(self):
		data = json.loads(self.ROW[2])
		for inspection in data['Inspections']:
			inspection = data['Inspections'][inspection]
			self.assertTrue(inspection['Date'])
			self.assertTrue(inspection['Summary'])

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
	description = 
	'''
		Unit test for Foodbot(s): To run, simply type 'python3 test_my_bot.py --file <db.foo_bar>'. This will check the 'testbots/' directory for the database file, and make sure that it is structured correctly for the SQLite -> Django parser. If it is not working as expected, make sure that the DB has data, that the DB is in 'testbots/', and that you are running the command from the 'testbots/' directory. A badbot is not a goodbot until it passes this test. Don't be a badbot.
	'''
	)
	parser.add_argument('--file', required=True, nargs='+', help='Filename to be passed')
	args = parser.parse_args()
	for f in args.file:
		if f in os.listdir('.'):
			conn = sqlite3.connect(('%s')%(f))
		else:
			print('ERROR: Could not connect to database,\n    Check that the name is correct and that it is in the "testbots/" directory')
			sys.exit(1)
		cur = conn.execute('select rowid, * from jsonfac')
		TestBot.ROW = cur.fetchone()
		unit_argv = [sys.argv[0]+f]
		unittest.main(argv=unit_argv)
