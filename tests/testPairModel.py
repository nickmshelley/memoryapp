from models.pairModel import Pair
import unittest
import datetime
from datetime import timedelta
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError


class TestPairModel(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		now = datetime.datetime.now() - datetime.timedelta(hours=6) # adjust for utc time
		self.date = now.date() # get rid of time information
		
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
	
	def testSetReviewFrequency(self):
		pairs = Pair.all().fetch(1000)
		pair = pairs[0]
		
		pair.numSuccesses = 0
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'daily')
		
		pair.numSuccesses = 1
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'daily')
		
		pair.numSuccesses = 6
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'daily')
		
		pair.numSuccesses = 7
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'daily')
		
		pair.numSuccesses = 8
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		
		pair.numSuccesses = 9
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		
		pair.numSuccesses = 11
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		
		pair.numSuccesses = 12
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		
		pair.numSuccesses = 13
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		
		pair.numSuccesses = 20
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		
		pair.numSuccesses = 24
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		
		pair.numSuccesses = 25
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		
		pair.numSuccesses = 26
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		
		pair.numSuccesses = 30
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		
		pair.numSuccesses = 60
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		
		pair.numSuccesses = 100
		pair.setReviewFrequency()
		self.assertEquals(pair.reviewFrequency, 'yearly')
	
	def testUpdateSuccesses(self):
		pairs = Pair.all().fetch(1000)
		pair = pairs[0]
		
		date = self.date
		
		pair.numSuccesses = 0
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 1)
		
		pair.numSuccesses = 1
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 2)
		
		pair.numSuccesses = 5
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 6)
		
		pair.numSuccesses = 6
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 7)
		
		pair.numSuccesses = 7
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 8)
		
		pair.numSuccesses = 8
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 9)
		
		pair.numSuccesses = 10
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'weekly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 11)
		
		pair.numSuccesses = 11
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 12)
		
		pair.numSuccesses = 12
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 13)
		
		pair.numSuccesses = 13
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 14)
		
		pair.numSuccesses = 20
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 21)
		
		pair.numSuccesses = 23
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'monthly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 24)
		
		pair.numSuccesses = 24
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 25)
		
		pair.numSuccesses = 25
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 26)
		
		pair.numSuccesses = 26
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 27)
		
		pair.numSuccesses = 30
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 31)
		
		pair.numSuccesses = 60
		pair.lastSuccess = date - timedelta(8)
		pair.updateSuccesses()
		self.assertEquals(pair.reviewFrequency, 'yearly')
		self.assertEquals(pair.lastSuccess, date)
		self.assertEquals(pair.numSuccesses, 61)
