from models.pairModel import Pair
from models.userPreferencesModel import UserPreferences
from models.categoryModel import Category
import unittest
import datetime
import os
from datetime import timedelta
from google.appengine.ext import db
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError
from google.appengine.api import user_service_stub 
from webtest import TestApp
from cards import application

class TestCategoryController(unittest.TestCase):
	def setUp(self):
		if 'datastore' in apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map:
			del apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['datastore']
		if 'datastore_v3' in apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map:
			del apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['datastore_v3']
		if 'user' in apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map:
			del apiproxy_stub_map.apiproxy._APIProxyStubMap__stub_map['user']
		
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore', stub)
		
		AUTH_DOMAIN = 'gmail.com' 
		LOGGED_IN_USER = 'test@example.com'
		apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
		os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
		os.environ['USER_EMAIL'] = LOGGED_IN_USER
		
		self.user = user = User(email = "test@example.com")
	
		self.app = TestApp(application)
		
		prefs = UserPreferences(user = user)
		prefs.put()
		
		category = Category(owner = user)
		category.name = 'Test'
		category.total = 9
		category.missed = 1
		category.correct = 7
		category.remaining = 2
		category.reviewTotal = 4
		category.reviewMissed = 1
		category.reviewCorrect = 2
		category.reviewRemaining = 2
		category.put()
		now = datetime.datetime.now() - datetime.timedelta(hours=6) # adjust for utc time
		date = now.date() # get rid of time information
		#not reviewing
		pair = Pair(owner = user, state = 'correct')
		pair.categories.append(category.key())
		pair.put()
		
		#daily
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date,
					state = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(100),
					state = 'correct', reviewState = 'missed', question = "telling", answer = "time")
		pair.categories.append(category.key())
		pair.put()
		
		#weekly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date,
					state = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(100),
					state = 'ready', reviewState = 'correct', question = "hi", answer = "there")
		pair.categories.append(category.key())
		pair.put()
		
		#monthly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date,
					state = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(100),
					state = 'missed', reviewState = 'ready', question = "specific", answer = "pile")
		pair.categories.append(category.key())
		pair.put()
		
		#yearly
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date,
					state = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(1000),
					state = 'correct', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		
		category = Category(owner = user)
		category.name = 'EditTest'
		category.description = "before description"
		category.put()
		
		category = Category(owner = user)
		category.name = 'DeleteTest'
		category.put()
		# add some pairs
		for i in range(5):
			pair = Pair(owner = user)
			pair.categories.append(category.key())
			pair.put()
	
	def testCategoryPage(self):
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		
		#test nonexistent category error
		response = self.app.get("/category?id=NOT-HERE")
		self.assertTrue("Category does not exist" in str(response))
		self.assertTrue("Total" not in str(response))
		
		#test category get
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("Total: 9" in str(response))
		self.assertTrue("Missed: 1" in str(response))
		self.assertTrue("Correct: 7" in str(response))
		self.assertTrue("Remaining: 2" in str(response))
		self.assertTrue("hi" in str(response))
		self.assertTrue("there" not in str(response))
		
		#test specific pair
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.missedPairs[0]
		response = self.app.get("/category?id=" + str(category.key()) + 
								";pair=" + str(pair.key()))
		self.assertTrue("specific" in str(response))
		
		#test show-answer
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		response = self.app.get("/category?id=" + str(category.key()) + 
								";pair=" + str(pair.key()) +
								";show-answer=True")
		self.assertTrue("there" in str(response))
		
		#test resetting
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		self.app.post('/update-pair', 
				{"pair": pair.key(), "state": "correct", "category": category.key()})
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("Total: 9" in str(response))
		self.assertTrue("Missed: 0" in str(response))
		self.assertTrue("Correct: 8" in str(response))
		self.assertTrue("Remaining: 1" in str(response))
		self.assertTrue("specific" in str(response))
		self.assertTrue("pile" not in str(response))
		
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		self.app.post('/update-pair', 
				{"pair": pair.key(), "state": "correct", "category": category.key()})
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("Total: 9" in str(response))
		self.assertTrue("Missed: 0" in str(response))
		self.assertTrue("Correct: 0" in str(response))
		self.assertTrue("Remaining: 9" in str(response))
		
		#test reviewing#####
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		category.reviewing = True
		category.put()
		#test category get
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("Total: 4" in str(response))
		self.assertTrue("Missed: 1" in str(response))
		self.assertTrue("Correct: 2" in str(response))
		self.assertTrue("Remaining: 2" in str(response))
		self.assertTrue("specific" in str(response))
		self.assertTrue("pile" not in str(response))
		
		#test specific pair
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.missedPairs[0]
		response = self.app.get("/category?id=" + str(category.key()) + 
								";pair=" + str(pair.key()))
		self.assertTrue("telling" in str(response))
		
		#test show-answer
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		response = self.app.get("/category?id=" + str(category.key()) + 
								";pair=" + str(pair.key()) +
								";show-answer=True")
		self.assertTrue("pile" in str(response))
		
		#test resetting
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		self.app.post('/update-pair', 
				{"pair": pair.key(), "state": "correct", "category": category.key()})
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("Total: 4" in str(response))
		self.assertTrue("Missed: 0" in str(response))
		self.assertTrue("Correct: 3" in str(response))
		self.assertTrue("Remaining: 1" in str(response))
		self.assertTrue("telling" in str(response))
		self.assertTrue("time" not in str(response))
		
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		pair = category.readyPairs[0]
		self.app.post('/update-pair', 
				{"pair": pair.key(), "state": "correct", "category": category.key()})
		response = self.app.get("/category?id=" + str(category.key()))
		response = self.app.get("/category?id=" + str(category.key()))
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		self.assertTrue("Total: 9" in str(response))
		self.assertTrue("Missed: 0" in str(response))
		self.assertTrue("Correct: 0" in str(response))
		self.assertTrue("Remaining: 9" in str(response))
		
		#test ownership error
		prefs =  UserPreferences(user = User(email = "notYours@example.com"))
		prefs.put()
		os.environ['USER_EMAIL'] = 'notYours@example.com'
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertTrue("You do not own this category" in str(response))
	
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
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		
		self.assertEquals(category.reviewing, False)
		self.assertEquals(category.reviewTotal, 4)
		self.assertEquals(category.reviewRemaining, 2)
		self.assertEquals(category.reviewMissed, 1)
		self.assertEquals(category.reviewCorrect, 2)
		
		self.app.post('/set-reviewing', {'category': category.key(), 'reviewing': category.reviewing})
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		self.assertEquals(category.reviewing, True)
		self.assertEquals(category.reviewTotal, 4)
		self.assertEquals(category.reviewRemaining, 4)
		self.assertEquals(category.reviewCorrect, 0)
		self.assertEquals(category.reviewMissed, 0)
		
		self.app.post('/set-reviewing', {'category': category.key(), 'reviewing': category.reviewing})
		categories = Category.all().filter('name =', 'Test').fetch(1000)
		category = categories[0]
		self.assertEquals(category.reviewing, False)
	
	def testEditCategoryForm(self):
		categories = Category.all().filter('name =', 'EditTest').fetch(1000)
		category = categories[0]
		
		response = self.app.get('/edit-category?id=' + str(category.key()))
		self.assertTrue("EditTest" in str(response))
		self.assertTrue("before description" in str(response))
	
	def testEditCategoryAction(self):
		categories = Category.all().filter('name =', 'EditTest').fetch(1000)
		category = categories[0]
		key = category.key()
		self.app.post('/change-category', {'id': category.key(),
													'name': "after name",
													'description': "after description",})
		category = Category.get(key)
		self.assertEquals("after name", category.name)
		self.assertEquals("after description", category.description)
	
	def testDeleteCategory(self):
		# get counts before deletions
		beforeCardCount = len(Pair.all().fetch(1000))
		beforeCategoryCount = len(Category.all().fetch(1000))
		# get category to delete
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		categoryKey = category.key()
		# get pair keys
		pairs = category.allPairs
		pairKeys = [pair.key() for pair in pairs]
		# get number of pairs in category
		toDelete = len(pairs)
		# perform delete
		self.app.get('/delete-category?category=' + str(category.key()))
		# get counts after deletion
		afterCardCount = len(Pair.all().fetch(1000))
		afterCategoryCount = len(Category.all().fetch(1000))
		# make sure numbers match up
		self.assertEquals(afterCardCount, beforeCardCount - toDelete)
		self.assertEquals(afterCategoryCount, beforeCategoryCount - 1)
		#make sure correct items were deleted
		for key in pairKeys:
			self.assertEquals(None, Pair.get(key))
		self.assertEquals(None, Category.get(categoryKey))
	
	def testViewCards(self):
		#set up a category with a bunch of pairs
		category = Category(owner = self.user)
		category.name = 'ViewTest'
		category.put()
		pairs = []
		# add some pairs
		for i in range(250):
			pair = Pair(owner = self.user)
			pair.categories.append(category.key())
			if i < 100:
				pair.question = "first"
				pair.reviewing = True
			elif i < 200:
				pair.question = "second"
			else:
				pair.question = "third"
				pair.reviewing = True
			pair.put()
		# test first page
		# default order should have non-reviewing ones first (the second 100)
		response = str(self.app.get('/view-pairs?category=' + str(category.key())))
		self.assertFalse('first' in response)
		self.assertTrue('second' in response)
		self.assertFalse('third' in response)
		self.assertTrue('Add to Review Schedule' in response)
		# test second page
		response = str(self.app.get('/view-pairs?category=' + str(category.key()) + '&page=next'))
		self.assertTrue('first' in response)
		self.assertFalse('second' in response)
		self.assertFalse('third' in response)
		self.assertFalse('Add to Review Schedule' in response)
		# test third page
		response = str(self.app.get('/view-pairs?category=' + str(category.key()) + '&page=next'))
		self.assertFalse('first' in response)
		self.assertFalse('second' in response)
		self.assertTrue('third' in response)
		self.assertFalse('Add to Review Schedule' in response)
