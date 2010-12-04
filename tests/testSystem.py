from models.categoryModel import Category
from models.pairModel import Pair
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

class TestMainPage(unittest.TestCase):
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
	
	def testReviewUseCase(self):
		self.app.post("/add-category", {'name': 'Test'})
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		key = category.key()
		
		response = self.app.get("/category?id=" + str(key))
		self.assertTrue("Total: 0" in str(response))
		
		# Make sure total gets updated correctly when a pair is added
		max = 7
		for i in range(1, max + 1):
			self.app.post('/add-pair', {'category': category.key(), 
										'question': 'a', 'answer': 'b'})
			response = self.app.get("/category?id=" + str(key))
			total = "Total: %d" % i
			self.assertTrue(total in str(response))
		
		# Make sure remaining, correct, and missed are correct
		remaining = "Remaining: %d" % max
		self.assertTrue(remaining in str(response))
		self.assertTrue("Correct: 0" in str(response))
		self.assertTrue("Missed: 0" in str(response))
		
		# Make sure missed and correct update properly (stop with one remaining)
		pairs = category.pairs
		numCorrect = 0
		numMissed = 0
		for i, p in zip(range(1, len(pairs)), pairs):
			state = 'missed'
			if i < (len(pairs) / 2):
				state = 'correct'
				numCorrect += 1
			else:
				numMissed += 1
			self.app.post('/update-pair', {'category': category.key(),
											'pair': p.key(),
											'state': state})
			response = str(self.app.get("/category?id=" + str(key)))
			total = "Total: %d" % max
			remaining = "Remaining: %d" % (max - i)
			missed = "Missed: %d" % numMissed
			correct = "Correct: %d" % numCorrect
			self.assertTrue(total in response)
			self.assertTrue(remaining in response)
			self.assertTrue(missed in response)
			self.assertTrue(correct in response)
		
		# Make sure the numbers reset correctly when 0 remaining
		p = pairs[len(pairs) - 1]
		self.app.post('/update-pair', {'category': category.key(),
										'pair': p.key(),
										'state': 'missed'})
		response = str(self.app.get("/category?id=" + str(key)))
		total = "Total: %d" % max
		remaining = "Remaining: %d" % (max - numCorrect)
		missed = "Missed: 0"
		correct = "Correct: %d" % numCorrect
		self.assertTrue(total in response)
		self.assertTrue(remaining in response)
		self.assertTrue(missed in response)
		self.assertTrue(correct in response)
