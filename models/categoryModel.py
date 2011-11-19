from google.appengine.ext import db
import datetime
import random
from models.pairModel import *
from models.userPreferencesModel import *

# State Pattern classes
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
	
	def addReviewed(self, cat, num):
		pass
	
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
	
	def nextPair(self, cat):
		return cat.nextNormalPair

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
	
	def addReviewed(self, cat, num):
		cat.reviewedThisSession += num
	
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
	
	def nextPair(self, cat):
		return cat.nextReviewPair

# Model class
class Category(db.Model):
	reviewState = ReviewState()
	nonReviewState = NonReviewState()
	
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
	reviewedThisSession = db.IntegerProperty(default=0)
	error = db.IntegerProperty(default = 0)
	
	reviewing = db.BooleanProperty(default=False)
	def getState(self):
		if self.reviewing:
			return Category.reviewState
		else:
			return Category.nonReviewState
	
	def setReviewing(self):
		self.reviewing = True
	
	def unsetReviewing(self):
		self.reviewing = False
	
	def setMissed(self, num):
		state = self.getState()
		state.setMissed(self, num)
	
	def addMissed(self, num):
		state = self.getState()
		state.addMissed(self, num)
	
	def setRemaining(self, num):
		state = self.getState()
		state.setRemaining(self, num)
	
	def addRemaining(self, num):
		state = self.getState()
		state.addRemaining(self, num)
	
	def setCorrect(self, num):
		state = self.getState()
		state.setCorrect(self, num)
	
	def addCorrect(self, num):
		state = self.getState()
		state.addCorrect(self, num)
	
	def addReviewed(self, num):
		state = self.getState()
		state.addReviewed(self, num)
	
	def getCounts(self):
		state = self.getState()
		return state.getCounts(self)
	
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
		state = self.getState()
		return state.pairs(self)
	
	@property
	def allPairs(self):
		query = Pair.all().filter('categories =', self.key())
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewPairs(self):
		pairs = self.getReviewPairs()
		return pairs
	
	@property
	def readyPairs(self):
		state = self.getState()
		return state.readyPairs(self)
	
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
		state = self.getState()
		return state.missedPairs(self)
	
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
		state = self.getState()
		return state.correctPairs(self)
	
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
	def nextPair(self):
		state = self.getState()
		return state.nextPair(self)
	
	@property
	def nextNormalPair(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'ready')
		query.order('order')
		pairs = query.fetch(1)
		if len(pairs) == 0:
			return None
		else:
			return pairs[0]
	
	#TODO change this to just do one pair once similar to above once query works (issue 33)
	@property
	def nextReviewPair(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'ready']
		if len(pairs) == 0:
			pair = None
		else:
			index = random.randint(0, len(pairs) - 1)
			pair = pairs[index]
		return pair
	
	def getReviewPairs(self):
		prefs = UserPreferences.all().filter('user =', users.get_current_user()).fetch(1)[0]
		offset = prefs.timeOffset
		limit = prefs.reviewLimit
		remaining = limit - self.reviewedThisSession
		pairs = []
		if remaining > 0:
			now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
			date = now.date() # get rid of time information
			query = Pair.all().filter('categories =', self.key())
			query.filter('nextReviewDate <=', date)
			query.order('nextReviewDate')
			query.order('numSuccesses')
			pairs = query.fetch(remaining)
		return pairs
	
	def resetPairs(self):
		doneReviewing = False
		changed = self.resetMissed()
		if not changed:
			changed = self.resetCorrect()
			if self.reviewing:
				self.unsetReviewing()
				doneReviewing = True
		return doneReviewing
	
	def resetMissed(self):
		pairs = []
		pairs = self.missedPairs
		self.setRemaining(0)
		changed = False
		while len(pairs) > 0:
			changed = True
			self.addRemaining(len(pairs))
			for pair in pairs:
				pair.setState('ready', self.reviewing)
				pair.put()
			pairs = self.missedPairs
		if changed:
			self.setMissed(0)
		return changed
	
	def resetCorrect(self):
		pairs = []
		pairs = self.correctPairs
		changed = False
		while len(pairs) > 0:
			changed = True
			self.addRemaining(len(pairs))
			for pair in pairs:
				pair.setState('ready', self.reviewing)
				pair.put()
			pairs = self.correctPairs
		if changed:
			self.setCorrect(0)
		return changed
	
	def deletePair(self, pair):
		self.total -= 1
		state = pair.state
		if state == 'missed':
			self.addMissed(-1)
		elif state == 'correct':
			self.addCorrect(-1)
		elif state == 'ready':
			self.addRemaining(-1)
		else:
			self.error += 1
		pair.delete()
