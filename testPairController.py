from pair import Pair
from category import Category
import unittest
import datetime
import os
from datetime import timedelta
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError
from google.appengine.api import user_service_stub 
from webtest import TestApp
from cards import application


class TestPairModel(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		AUTH_DOMAIN = 'gmail.com' 
		LOGGED_IN_USER = 'test@example.com'
		apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
		os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
		os.environ['USER_EMAIL'] = LOGGED_IN_USER
		
		self.user = user = User(email = "test@example.com")
		category = Category(owner = user)
		category.name = 'AddTest'
		category.put()
		
		category = Category(owner = user)
		category.name = 'UpdateTest'
		category.remaining = 1
		category.reviewRemaining = 1
		category.put()
		pair = Pair(owner = user)
		pair.categories.append(category.key())
		pair.put()
	
		self.app = TestApp(application)
	
	def testAddPairAction(self):
		categories = Category.all().filter('name =', 'AddTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allPairs
		self.assertEquals(len(pairs), 0)
		self.assertEquals(category.total, 0)
		self.assertEquals(category.remaining, 0)
		
		self.app.post('/add-pair', {'category': category.key(), 'question': 'a', 'answer': 'b'})
		pairs = category.allPairs
		categories = Category.all().filter('name =', 'AddTest').fetch(1000)
		category = categories[0]
		self.assertEquals(len(pairs), 1)
		self.assertEquals(category.total, 1)
		self.assertEquals(category.remaining, 1)
		pair = pairs[0]
		self.assertEquals(pair.categories[0], category.key())
		self.assertEquals(pair.owner, self.user)
		self.assertEquals(pair.question, 'a')
		self.assertEquals(pair.answer, 'b')
	
	def testUpdatePairAction(self):
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(category.correct, 0)
		self.assertEquals(category.reviewCorrect, 0)
		self.assertEquals(category.missed, 0)
		self.assertEquals(category.reviewMissed, 0)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.reviewRemaining, 1)
		self.assertEquals(category.error, 0)
		self.assertEquals(pair.state, 'ready')
		self.assertEquals(pair.reviewState, 'ready')
		
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'missed'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'ready')
		self.assertEquals(pair.state, 'missed')
		self.assertEquals(category.reviewMissed, 0)
		self.assertEquals(category.missed, 1)
		self.assertEquals(category.reviewRemaining, 1)
		self.assertEquals(category.remaining, 0)
		
		category.missed = 0
		category.remaining = 1
		pair.state = 'ready'
		category.put()
		pair.put()
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'correct'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'ready')
		self.assertEquals(pair.state, 'correct')
		self.assertEquals(category.reviewCorrect, 0)
		self.assertEquals(category.correct, 1)
		self.assertEquals(category.reviewRemaining, 1)
		self.assertEquals(category.remaining, 0)
		self.assertEquals(pair.numSuccesses, 0)
		self.assertEquals(pair.lastSuccess, None)
		self.assertEquals(pair.reviewFrequency, None)
		
		
		category.correct = 0
		category.remaining = 1
		category.reviewing = True
		pair.state = 'ready'
		category.put()
		pair.put()
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'missed'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'missed')
		self.assertEquals(pair.state, 'ready')
		self.assertEquals(category.reviewMissed, 1)
		self.assertEquals(category.missed, 0)
		self.assertEquals(category.reviewRemaining, 0)
		self.assertEquals(category.remaining, 1)
		
		category.reviewMissed = 0
		category.reviewRemaining = 1
		pair.reviewState = 'ready'
		category.put()
		pair.put()
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'correct'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'correct')
		self.assertEquals(pair.state, 'ready')
		self.assertEquals(category.reviewCorrect, 1)
		self.assertEquals(category.correct, 0)
		self.assertEquals(category.reviewRemaining, 0)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(pair.numSuccesses, 1)
		self.assertEquals(pair.lastSuccess, datetime.date.today())
		self.assertEquals(pair.reviewFrequency, 'daily')
		
		category.reviewCorrect = 0
		category.reviewRemaining = 1
		pair.reviewState = 'ready'
		category.put()
		pair.put()
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'something'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'something')
		self.assertEquals(pair.state, 'ready')
		self.assertEquals(category.reviewMissed, 0)
		self.assertEquals(category.missed, 0)
		self.assertEquals(category.reviewRemaining, 0)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.error, 1)
	
	def testMarkReviewAction(self):
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		
		self.assertEquals(category.correct, 0)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(pair.reviewing, False)
		self.assertEquals(pair.firstSuccess, None)
		self.assertEquals(pair.lastSuccess, None)
		self.assertEquals(pair.numSuccesses, 0)
		self.assertEquals(pair.reviewFrequency, None)
		self.assertEquals(pair.state, 'ready')
		
		self.app.post('/mark-review', {'category': category.key(), 'pair': pair.key()})
		
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(category.correct, 1)
		self.assertEquals(category.remaining, 0)
		self.assertEquals(pair.reviewing, True)
		self.assertEquals(pair.firstSuccess, datetime.date.today())
		self.assertEquals(pair.lastSuccess, datetime.date.today())
		self.assertEquals(pair.numSuccesses, 1)
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.state, 'correct')
