from models.pairModel import Pair
from models.categoryModel import Category
from models.userPreferencesModel import UserPreferences
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


class TestPairController(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		AUTH_DOMAIN = 'gmail.com' 
		LOGGED_IN_USER = 'test@example.com'
		apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
		os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
		os.environ['USER_EMAIL'] = LOGGED_IN_USER
		
		now = datetime.datetime.now() - datetime.timedelta(hours=6) # adjust for utc time
		self.date = now.date() # get rid of time information
		
		self.user = user = User(email = "test@example.com")
		
		prefs = UserPreferences(user = user)
		prefs.put()
		
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
		
		category = Category(owner = user)
		category.name = 'EditTest'
		category.put()
		pair = Pair(owner = user)
		pair.question = "before question"
		pair.answer = "before answer"
		pair.categories.append(category.key())
		pair.put()
		
		category = Category(owner = user)
		category.name = 'DeleteTest'
		category.total =  6
		category.missed = 2
		category.correct = 2
		category.remaining = 2
		category.put()
		# add a couple ready pairs
		pair = Pair(owner = user)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user)
		pair.categories.append(category.key())
		pair.put()
		# add a couple missed pair
		pair = Pair(owner = user)
		pair.state = 'missed'
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user)
		pair.state = 'missed'
		pair.categories.append(category.key())
		pair.put()
		# add a couple correct pair
		pair = Pair(owner = user)
		pair.state = 'correct'
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user)
		pair.state = 'correct'
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
		self.assertEquals(pair.order, 0)
		
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'missed'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(pair.reviewState, 'ready')
		self.assertEquals(pair.state, 'missed')
		self.assertNotEquals(pair.order, 0)
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
		category.setReviewing()
		pair.state = 'ready'
		category.put()
		pair.put()
		self.app.post('/update-pair', {'category': category.key(), 'pair': pair.key(),
										'state': 'missed'})
		categories = Category.all().filter('name =', 'UpdateTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals(category.reviewing, True)
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
		self.assertEquals(pair.lastSuccess, self.date)
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
		self.assertEquals(category.correct, 0)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(pair.reviewing, True)
		self.assertEquals(pair.firstSuccess, self.date)
		self.assertEquals(pair.lastSuccess, self.date)
		self.assertEquals(pair.numSuccesses, 1)
		self.assertEquals(pair.reviewFrequency, 'daily')
		self.assertEquals(pair.state, 'ready')
	
	def testEditPairForm(self):
		categories = Category.all().filter('name =', 'EditTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		
		response = self.app.get('/edit-pair?pair=' + str(pair.key()) + 
								';category=' + str(category.key()))
		self.assertTrue("before question" in str(response))
		self.assertTrue("before answer" in str(response))
	
	def testEditPairAction(self):
		categories = Category.all().filter('name =', 'EditTest').fetch(1000)
		category = categories[0]
		pairs = category.allPairs
		pair = pairs[0]
		
		self.app.post('/change-pair', {'id': pair.key(),
													'category': category.key(),
													'question': "after question",
													'answer': "after answer",})
		pairs = category.allPairs
		pair = pairs[0]
		self.assertEquals("after question", pair.question)
		self.assertEquals("after answer", pair.answer)
	
	#TODO some of this stuff tests the model helper function; consider moving 
	def testDeletePair(self):
		# get count before deletions
		beforeCount = len(Pair.all().fetch(1000))
		# test delete in normal mode
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		# make sure category counts are what we expect before hand
		self.assertEquals(category.total, 6)
		self.assertEquals(category.remaining, 2)
		self.assertEquals(category.correct, 2)
		self.assertEquals(category.missed, 2)
		# make sure pairs in sets are what we expect before hand
		self.assertEquals(len(category.allPairs), 6)
		self.assertEquals(len(category.readyPairs), 2)
		self.assertEquals(len(category.correctPairs), 2)
		self.assertEquals(len(category.missedPairs), 2)
		
		# test deleting a ready pair
		pairs = category.readyPairs
		pair = pairs[0]
		self.app.get('/delete-pair?pair=' + str(pair.key()) + ';category=' + str(category.key()))
		pair = Pair.get(pair.key())
		self.assertEquals(pair, None)
		# check counts
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		afterCount = len(Pair.all().fetch(1000))
		self.assertEquals(beforeCount - 1, afterCount)
		# reset beforeCount for next test
		beforeCount = afterCount
		self.assertEquals(category.total, 5)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.correct, 2)
		self.assertEquals(category.missed, 2)
		self.assertEquals(len(category.allPairs), 5)
		self.assertEquals(len(category.readyPairs), 1)
		self.assertEquals(len(category.correctPairs), 2)
		self.assertEquals(len(category.missedPairs), 2)
		
		# test deleting a correct pair
		pairs = category.correctPairs
		pair = pairs[0]
		self.app.get('/delete-pair?pair=' + str(pair.key()) + ';category=' + str(category.key()))
		pair = Pair.get(pair.key())
		self.assertEquals(pair, None)
		# check counts
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		afterCount = len(Pair.all().fetch(1000))
		self.assertEquals(beforeCount - 1, afterCount)
		# reset beforeCount for next test
		beforeCount = afterCount
		self.assertEquals(category.total, 4)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.correct, 1)
		self.assertEquals(category.missed, 2)
		self.assertEquals(len(category.allPairs), 4)
		self.assertEquals(len(category.readyPairs), 1)
		self.assertEquals(len(category.correctPairs), 1)
		self.assertEquals(len(category.missedPairs), 2)
		
		# test deleting a missed pair
		pairs = category.missedPairs
		pair = pairs[0]
		self.app.get('/delete-pair?pair=' + str(pair.key()) + ';category=' + str(category.key()))
		pair = Pair.get(pair.key())
		self.assertEquals(pair, None)
		# check counts
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		afterCount = len(Pair.all().fetch(1000))
		self.assertEquals(beforeCount - 1, afterCount)
		# reset beforeCount for next test
		beforeCount = afterCount
		self.assertEquals(category.total, 3)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.correct, 1)
		self.assertEquals(category.missed, 1)
		self.assertEquals(len(category.allPairs), 3)
		self.assertEquals(len(category.readyPairs), 1)
		self.assertEquals(len(category.correctPairs), 1)
		self.assertEquals(len(category.missedPairs), 1)
		
		# test that deleting the last ready pair calls reset correctly
		pairs = category.readyPairs
		pair = pairs[0]
		self.app.get('/delete-pair?pair=' + str(pair.key()) + ';category=' + str(category.key()))
		self.app.get('/category?id=' + str(category.key()))
		pair = Pair.get(pair.key())
		self.assertEquals(pair, None)
		# check counts
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		afterCount = len(Pair.all().fetch(1000))
		self.assertEquals(beforeCount - 1, afterCount)
		# reset beforeCount for next test
		beforeCount = afterCount
		self.assertEquals(category.total, 2)
		self.assertEquals(category.remaining, 1)
		self.assertEquals(category.correct, 1)
		self.assertEquals(category.missed, 0)
		self.assertEquals(len(category.allPairs), 2)
		self.assertEquals(len(category.readyPairs), 1)
		self.assertEquals(len(category.correctPairs), 1)
		self.assertEquals(len(category.missedPairs), 0)
		
		# test that delete is not an option in review mode
		categories = Category.all().filter('name =', 'DeleteTest').fetch(1000)
		category = categories[0]
		category.reviewing = True
		category.put()
		response = self.app.get("/category?id=" + str(category.key()))
		self.assertFalse("Delete" in str(response))
