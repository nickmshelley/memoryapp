from google.appengine.ext import db
import datetime
from pairModel import *	

class Category(db.Model):
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
	
	def setMissed(self, num):
		if self.reviewing:
			self.reviewMissed = num
		else:
			self.missed = num
	
	def addMissed(self, num):
		if self.reviewing:
			self.reviewMissed += num
		else:
			self.missed += num
	
	def setRemaining(self, num):
		if self.reviewing:
			self.reviewRemaining = num
		else:
			self.remaining = num
	
	def addRemaining(self, num):
		if self.reviewing:
			self.reviewRemaining += num
		else:
			self.remaining += num
	
	def setCorrect(self, num):
		if self.reviewing:
			self.reviewCorrect = num
		else:
			self.correct = num
	
	def addCorrect(self, num):
		if self.reviewing:
			self.reviewCorrect += num
		else:
			self.correct += num
	
	def getCounts(self):
		if self.reviewing:
			return self.getReviewCounts()
		else:
			return self.getAllCounts()
	
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
		if self.reviewing:
			return self.reviewPairs
		else:
			return self.allPairs
	
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
		if self.reviewing:
			return self.reviewReadyPairs
		else:
			return self.allReadyPairs
	
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
		if self.reviewing:
			return self.reviewMissedPairs
		else:
			return self.allMissedPairs
	
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
		if self.reviewing:
			return self.reviewCorrectPairs
		else:
			return self.allCorrectPairs
	
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