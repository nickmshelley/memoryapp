from pair import Pair
import unittest
import datetime
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError


class TestPairModel(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		user = user = User(email = "test@foo.com")
		pair = Pair(owner = user)
		pair.put()
	
	def testCreation(self):
		user = User(email = "test@foo.com")
		self.assertRaises(BadValueError, Pair)
		
		pair = Pair(owner = user)
		self.assertEquals(pair.owner, user)
		self.assertEquals(pair.state, 'ready')
		self.assertEquals(pair.reviewState, 'ready')
		self.assertEquals(pair.reviewing, False)
		self.assertEquals(pair.numSuccesses, 0)
		
		date = datetime.date(1986, 7, 16)
		pair = Pair(owner = user, reviewing = True, numSuccesses = 10, lastSuccess = date,
					state = 'Missed', reviewState = 'Correct')
		self.assertEquals(pair.owner, user)
		self.assertEquals(pair.reviewing, True)
		self.assertEquals(pair.numSuccesses, 10)
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.state, 'Missed')
		self.assertEquals(pair.reviewState, 'Correct')
	
	def testSetState(self):
		pairs = Pair.all().fetch(1000)
		pair = pairs[0]
		
		pair.setState('missed', False)
		self.assertEquals(pair.state, 'missed')
		self.assertEquals(pair.reviewState, 'ready')
		
		pair.setState('correct', True)
		self.assertEquals(pair.reviewState, 'correct')
		self.assertEquals(pair.state, 'missed')