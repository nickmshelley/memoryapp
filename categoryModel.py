from google.appengine.ext import db
import datetime
from pairModel import *

class NonReviewState:
	def setMissed(self, cat, num):
		cat.missed = num
	
	def addMissed(self, cat, num):
		cat.missed += num
	
	def setRemaining(self, cat, num):
		cat.remaining = num
	
	def addRemaining(self, cat, num):
		cat.remaining += num
	
	def setCorrect(self, cat, num):
		cat.correct = num
	
	def addCorrect(self, cat, num):
		cat.correct += num
	
	def getCounts(self, cat):
		return cat.getAllCounts()
	
	def pairs(self, cat):
		return cat.allPairs
	
	def readyPairs(self, cat):
		return cat.allReadyPairs
	
	def missedPairs(self, cat):
		return cat.allMissedPairs
	
	def correctPairs(self, cat):
		return cat.allCorrectPairs

class ReviewState:
	def setMissed(self, cat, num):
		cat.reviewMissed = num
	
	def addMissed(self, cat, num):
		cat.reviewMissed += num
	
	def setRemaining(self, cat, num):
		cat.reviewRemaining = num
	
	def addRemaining(self, cat, num):
		cat.reviewRemaining += num
	
	def setCorrect(self, cat, num):
		cat.reviewCorrect = num
	
	def addCorrect(self, cat, num):
		cat.reviewCorrect += num
	
	def getCounts(self, cat):
		return cat.getReviewCounts()
	
	def pairs(self, cat):
		return cat.reviewPairs
	
	def readyPairs(self, cat):
		return cat.reviewReadyPairs
	
	def missedPairs(self, cat):
		return cat.reviewMissedPairs
	
	def correctPairs(self, cat):
		return cat.reviewCorrectPairs

class Category(db.Model):
	reviewState = ReviewState()
	nonReviewState = NonReviewState()
	state = nonReviewState
	
	name = db.StringProperty()
	owner = db.UserProperty(required = True)
	description = db.TextProperty()
	
	# Category meta information
	total = db.IntegerProperty(default=0)
	missed = db.IntegerProperty(default=0)
	correct = db.IntegerProperty(default=0)
	remaining = db.IntegerProperty(default=0)
	reviewTotal = db.IntegerProperty(default=0)
	reviewMissed = db.IntegerProperty(default=0)
	reviewCorrect = db.IntegerProperty(default=0)
	reviewRemaining = db.IntegerProperty(default=0)
	error = db.IntegerProperty(default = 0)
	
	reviewing = db.BooleanProperty(default=False)
	
	def setReviewing(self):
		self.reviewing = True
		self.state = reviewState
	
	def unsetReviewing(self):
		self.reviewing = False
		self.state = nonReviewState
	
	def setMissed(self, num):
		self.state.setMissed(self, num)
	
	def addMissed(self, num):
		self.state.addMissed(self, num)
	
	def setRemaining(self, num):
		self.state.setRemaining(self, num)
	
	def addRemaining(self, num):
		self.state.addRemaining(self, num)
	
	def setCorrect(self, num):
		self.state.setCorrect(self, num)
	
	def addCorrect(self, num):
		self.state.addCorrect(self, num)
	
	def getCounts(self):
		return self.state.getCounts(self)
	
	def getAllCounts(self):
		counts = {
				'total': self.total,
				'missed': self.missed,
				'correct': self.correct,
				'remaining': self.remaining,
				}
		return counts
	
	def getReviewCounts(self):
		counts = {
				'total': self.reviewTotal,
				'missed': self.reviewMissed,
				'correct': self.reviewCorrect,
				'remaining': self.reviewRemaining,
				}
		return counts
	
	@property
	def pairs(self):
		return self.state.pairs(self)
	
	@property
	def allPairs(self):
		query = Pair.all().filter('categories =', self.key())
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewPairs(self):
		pairs = self.dailyReviewPairs + \
				self.weeklyReviewPairs + \
				self.monthlyReviewPairs + \
				self.yearlyReviewPairs
		return pairs
	
	@property
	def readyPairs(self):
		return self.state.readyPairs(self)
	
	@property
	def allReadyPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'ready')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewReadyPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'ready']
		#pairs = filter(lambda p: p.state == 'ready', allPairs)
		return pairs
	
	@property
	def missedPairs(self):
		return self.state.missedPairs(self)
	
	@property
	def allMissedPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'missed')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewMissedPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'missed']
		#pairs = filter(lambda p: p.state == 'missed', allPairs)
		return pairs
	
	@property
	def correctPairs(self):
		return self.state.correctPairs(self)
	
	@property
	def allCorrectPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'correct')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewCorrectPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'correct']
		#pairs = filter(lambda p: p.state == 'correct', allPairs)
		return pairs
	
	@property
	def dailyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(1)
		pairs = self.getReviewPairs('daily', date)
		return pairs
	
	@property
	def weeklyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(7)
		pairs = self.getReviewPairs('weekly', date)
		return pairs
	
	@property
	def monthlyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(30)
		pairs = self.getReviewPairs('monthly', date)
		return pairs
	
	@property
	def yearlyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(365)
		pairs = self.getReviewPairs('yearly', date)
		return pairs
	
	def getReviewPairs(self, frequency, date):
		query = Pair.all().filter('categories =', self.key())
		query.filter('reviewFrequency =', frequency)
		query.filter('lastSuccess <=', date)
		pairs = query.fetch(1000)
		return pairs