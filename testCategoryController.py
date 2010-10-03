from pairModel import Pair
from categoryModel import Category
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

class TestCategoryController(unittest.TestCase):
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
	
		self.app = TestApp(application)
		
		category = Category(owner = user)
		category.name = 'SetReviewTest'
		category.put()
		now = datetime.datetime.now() - datetime.timedelta(hours=6) # adjust for utc time
		date = now.date() # get rid of time information
		#not reviewing
		pair = Pair(owner = user)
		pair.categories.append(category.key())
		pair.put()
		
		#daily
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(100),
					state = 'correct', reviewState = 'missed')
		pair.categories.append(category.key())
		pair.put()
		
		#weekly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(100),
					state = 'ready', reviewState = 'missed')
		pair.categories.append(category.key())
		pair.put()
		
		#monthly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(100),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		
		#yearly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(1000),
					state = 'correct', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
	
	def testAddCategoryAction(self):
		user = User(email = "addTest@example.com")
		os.environ['USER_EMAIL'] = 'addTest@example.com'
	
		categories = Category.all().filter('owner =', user).fetch(10)
		self.assertEquals(len(categories), 0)
		
		self.app.post('/add-category', {'name': 'AddTest', 'description': 'my description'})
		categories = Category.all().filter('owner =', user).fetch(1000)
		category = categories[0]
		self.assertEquals(category.name, 'AddTest')
		self.assertEquals(category.description, 'my description')
		self.assertEquals(category.owner, user)
		
		self.app.post('/add-category', {'description': 'another description'})
		categories = Category.all().filter('owner =', user).fetch(1000)
		category = categories[1]
		self.assertEquals(len(categories), 2)
		self.assertEquals(category.name, 'Untitled Category')
		self.assertEquals(category.description, 'another description')
		self.assertEquals(category.owner, user)
	
	def testSetReviewingAction(self):
		categories = Category.all().filter('name =', 'SetReviewTest').fetch(1000)
		category = categories[0]
		
		self.assertEquals(category.reviewing, False)
		self.assertEquals(category.reviewTotal, 0)
		self.assertEquals(category.reviewRemaining, 0)
		self.assertEquals(category.reviewMissed, 0)
		self.assertEquals(category.reviewCorrect, 0)
		
		self.app.post('/set-reviewing', {'category': category.key(), 'reviewing': category.reviewing})
		categories = Category.all().filter('name =', 'SetReviewTest').fetch(1000)
		category = categories[0]
		self.assertEquals(category.reviewing, True)
		self.assertEquals(category.reviewTotal, 4)
		self.assertEquals(category.reviewRemaining, 4)
		self.assertEquals(category.reviewCorrect, 0)
		self.assertEquals(category.reviewMissed, 0)
		
		self.app.post('/set-reviewing', {'category': category.key(), 'reviewing': category.reviewing})
		categories = Category.all().filter('name =', 'SetReviewTest').fetch(1000)
		category = categories[0]
		self.assertEquals(category.reviewing, False)