from category import Category
from pair import Pair
import datetime
from datetime import timedelta
import unittest
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError


class TestCategoryModel(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		user = user = User(email = "test@foo.com")
		category = Category(owner = user)
		category.name = 'MetaTests'
		category.put()
		for i in range(5):
			pair = Pair(owner = user)
			pair.categories.append(category.key())
			pair.put()
		
		category = Category(owner = user)
		category.name = 'AllPairsTest'
		category.put()
		for i in range(10):
			pair = Pair(owner = user)
			pair.categories.append(category.key())
			pair.put()
		
		category = Category(owner = user)
		category.name = 'RetrievalTest'
		category.put()
		date = datetime.date.today()
		#not reviewing
		pair = Pair(owner = user)
		pair.categories.append(category.key())
		pair.put()
		
		#daily
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date)
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date + timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(1),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(2),
					state = 'ready', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(5),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(7),
					state = 'ready', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'daily', lastSuccess = date - timedelta(8),
					state = 'missed', reviewState = 'ready')
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
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date + timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(2))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(6))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(7),
					state = 'ready', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(8),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(9),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(30),
					state = 'correct', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'weekly', lastSuccess = date - timedelta(50),
					state = 'missed', reviewState = 'correct')
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
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date + timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(7))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(29))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(30),
					state = 'ready', reviewState = 'missed')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(31),
					state = 'ready', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(32),
					state = 'correct', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(60),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'monthly', lastSuccess = date - timedelta(61),
					state = 'missed', reviewState = 'correct')
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
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date + timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(1))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(30))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(364))
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(365),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(366),
					state = 'missed', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(367),
					state = 'ready', reviewState = 'missed')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(600),
					state = 'missed', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(730),
					state = 'ready', reviewState = 'correct')
		pair.categories.append(category.key())
		pair.put()
		pair = Pair(owner = user, reviewing = True, reviewFrequency = 'yearly', lastSuccess = date - timedelta(1000),
					state = 'correct', reviewState = 'ready')
		pair.categories.append(category.key())
		pair.put()
		
	def testCreation(self):
		user = User(email = "test@foo.com")
		self.assertRaises(BadValueError, Category)
		
		category = Category(owner = user)
		self.assertEquals(category.owner, user)
		self.assertEquals(category.total, 0)
		self.assertEquals(category.missed, 0)
		self.assertEquals(category.correct, 0)
		self.assertEquals(category.remaining, 0)
		self.assertEquals(category.reviewTotal, 0)
		self.assertEquals(category.reviewMissed, 0)
		self.assertEquals(category.reviewCorrect, 0)
		self.assertEquals(category.reviewRemaining, 0)
		self.assertEquals(category.error, 0)
		self.assertEquals(category.reviewing, False)
	
	def testSetMissed(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.setMissed(4)
		self.assertEquals(category.missed, 4)
		self.assertEquals(category.reviewMissed, 0)
		
		category.reviewing = True
		category.setMissed(8)
		self.assertEquals(category.missed, 4)
		self.assertEquals(category.reviewMissed, 8)
	
	def testAddMissed(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.addMissed(2)
		self.assertEquals(category.missed, 2)
		self.assertEquals(category.reviewMissed, 0)
		
		category.addMissed(-1)
		self.assertEquals(category.missed, 1)
		
		category.reviewing = True
		category.addMissed(4)
		self.assertEquals(category.reviewMissed, 4)
		self.assertEquals(category.missed, 1)
		
		category.addMissed(-2)
		self.assertEquals(category.reviewMissed, 2)

	def testSetRemaining(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.setRemaining(4)
		self.assertEquals(category.remaining, 4)
		self.assertEquals(category.reviewRemaining, 0)
		
		category.reviewing = True
		category.setRemaining(8)
		self.assertEquals(category.remaining, 4)
		self.assertEquals(category.reviewRemaining, 8)
	
	def testAddRemaining(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.addRemaining(2)
		self.assertEquals(category.remaining, 2)
		self.assertEquals(category.reviewRemaining, 0)
		
		category.addRemaining(-1)
		self.assertEquals(category.remaining, 1)
		
		category.reviewing = True
		category.addRemaining(4)
		self.assertEquals(category.reviewRemaining, 4)
		self.assertEquals(category.remaining, 1)
		
		category.addRemaining(-2)
		self.assertEquals(category.reviewRemaining, 2)

	def testSetCorrect(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.setCorrect(4)
		self.assertEquals(category.correct, 4)
		self.assertEquals(category.reviewCorrect, 0)
		
		category.reviewing = True
		category.setCorrect(8)
		self.assertEquals(category.correct, 4)
		self.assertEquals(category.reviewCorrect, 8)
	
	def testAddCorrect(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.addCorrect(2)
		self.assertEquals(category.correct, 2)
		self.assertEquals(category.reviewCorrect, 0)
		
		category.addCorrect(-1)
		self.assertEquals(category.correct, 1)
		
		category.reviewing = True
		category.addCorrect(4)
		self.assertEquals(category.reviewCorrect, 4)
		self.assertEquals(category.correct, 1)
		
		category.addCorrect(-2)
		self.assertEquals(category.reviewCorrect, 2)
	
	def testGetAllCounts(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.total = 2
		category.missed = 4
		category.correct = 6
		category.remaining = 8
		answer = {'total': 2, 'missed': 4, 'correct': 6, 'remaining': 8}
		
		response = category.getAllCounts()
		self.assertEquals(response, answer)
	
	def testGetReviewCounts(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.reviewTotal = 1
		category.reviewMissed = 3
		category.reviewCorrect = 5
		category.reviewRemaining = 7
		answer = {'total': 1, 'missed': 3, 'correct': 5, 'remaining': 7}
		
		response = category.getReviewCounts()
		self.assertEquals(response, answer)
	
	def testGetCounts(self):
		categories = Category.all().filter('name =', 'MetaTests').fetch(1000)
		category = categories[0]
		
		category.total = 2
		category.missed = 4
		category.correct = 6
		category.remaining = 8
		category.reviewTotal = 1
		category.reviewMissed = 3
		category.reviewCorrect = 5
		category.reviewRemaining = 7
		
		nonReviewAnswer = {'total': 2, 'missed': 4, 'correct': 6, 'remaining': 8}
		reviewAnswer = {'total': 1, 'missed': 3, 'correct': 5, 'remaining': 7}
		
		response = category.getCounts()
		self.assertEquals(response, nonReviewAnswer)
		
		category.reviewing = True
		response = category.getCounts()
		self.assertEquals(response, reviewAnswer)
	
	def testPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.pairs
		self.assertEquals(len(pairs), 43)
		
		category.reviewing = True
		pairs = category.pairs
		self.assertEquals(len(pairs), 24)
	
	def testAllPairs(self):
		categories = Category.all().filter('name =', 'AllPairsTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allPairs
		self.assertEquals(len(pairs), 10)
	
	def testGetReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		date = datetime.date.today()
		
		pairs = category.getReviewPairs('daily', date - timedelta(1))
		self.assertEquals(len(pairs), 6)
		
		pairs = category.getReviewPairs('weekly', date - timedelta(7))
		self.assertEquals(len(pairs), 6)
		
		pairs = category.getReviewPairs('monthly', date - timedelta(30))
		self.assertEquals(len(pairs), 6)
		
		pairs = category.getReviewPairs('yearly', date - timedelta(365))
		self.assertEquals(len(pairs), 6)
		
	def testDailyReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.dailyReviewPairs
		self.assertEquals(len(pairs), 6)
	
	def testWeeklyReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.weeklyReviewPairs
		self.assertEquals(len(pairs), 6)
	
	def testMonthlyReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.monthlyReviewPairs
		self.assertEquals(len(pairs), 6)
	
	def testYearlyReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.yearlyReviewPairs
		self.assertEquals(len(pairs), 6)
	
	def testReviewPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.reviewPairs
		self.assertEquals(len(pairs), 24)
	
	def testReadyPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.readyPairs
		self.assertEquals(len(pairs), 27)
		
		category.reviewing = True
		pairs = category.readyPairs
		self.assertEquals(len(pairs), 12)
	
	def testAllReadyPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allReadyPairs
		self.assertEquals(len(pairs), 27)
	
	def testReviewReadyPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.reviewReadyPairs
		self.assertEquals(len(pairs), 12)
	
	def testMissedPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.missedPairs
		self.assertEquals(len(pairs), 12)
		
		category.reviewing = True
		pairs = category.missedPairs
		self.assertEquals(len(pairs), 4)
	
	def testAllMissedPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allMissedPairs
		self.assertEquals(len(pairs), 12)
		
	def testReviewMissedPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.reviewMissedPairs
		self.assertEquals(len(pairs), 4)
	
	def testCorrectPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.correctPairs
		self.assertEquals(len(pairs), 4)
		
		category.reviewing = True
		pairs = category.correctPairs
		self.assertEquals(len(pairs), 8)
	
	def testAllCorrectPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.allCorrectPairs
		self.assertEquals(len(pairs), 4)
	
	def testReviewCorrectPairs(self):
		categories = Category.all().filter('name =', 'RetrievalTest').fetch(1000)
		category = categories[0]
		
		pairs = category.reviewCorrectPairs
		self.assertEquals(len(pairs), 8)
