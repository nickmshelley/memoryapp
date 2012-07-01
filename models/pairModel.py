from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from models.userPreferencesModel import UserPreferences
import datetime

class Pair(db.Model):
	owner = db.UserProperty(required = True)
	
	# random number used to create random order (done this way for performance)
	order = db.IntegerProperty(default = 0)
	
	# Pair info
	question = db.StringProperty()
	answer = db.TextProperty()
	state = db.CategoryProperty(default = 'ready') #missed or ready
	numSuccesses = db.IntegerProperty(default = 0)
	reverseState = db.CategoryProperty(default = 'ready') #missed or ready
	reverseNumSuccesses = db.IntegerProperty(default = 0)
	
	# Date info
	lastSuccess = db.DateProperty()
	nextReviewDate = db.DateProperty()
	lastReverseSuccess = db.DateProperty()
	nextReverseReviewDate = db.DateProperty()
	
	# Category Affiliation
	categories = db.ListProperty(db.Key)
	
	def updateDbAndCache(self, category_key, reverse):
		self.put()
		key = str(category_key) + "reviewPairs"
		pairs = memcache.get(key)
		if pairs is not None:
			tempPairs = [p for p in pairs if str(self.key()) == str(p.key())]
			if len(tempPairs) > 1:
				print "should only match one but matches %d" % len(tempPairs)
			try:
				pairs.remove(tempPairs[0])
				#insert at end of missed
				if reverse:
					if self.reverseState == 'missed':
						self.insertAfterMissed(pairs, reverse)
				else:
					if self.state == 'missed':
						self.insertAfterMissed(pairs, reverse)
				memcache.set(key, pairs)
			except:
				pass
	
	def insertAfterMissed(self, pairs, reverse):
		for i in range(len(pairs)):
			state = None
			if reverse:
				state = pairs[i].reverseState
			else:
				state = pairs[i].state
			if state == 'ready':
				pairs.insert(i, self)
				return
		#if all missed
		pairs.append(self)
	
	def updateMisses(self, reverse):
		if reverse:
			self.reverseNumSuccesses -= 2;
			if self.reverseNumSuccesses < 0:
				self.reverseNumSuccesses = 0
		else:
			self.numSuccesses -= 2;
			if self.numSuccesses < 0:
				self.numSuccesses = 0
	
	def updateSuccesses(self, reverse):
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		
		now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		today = now.date() # get rid of time information
		if reverse:
			self.reverseNumSuccesses += 1
			self.lastReverseSuccess = today
			self.setNextReview(reverse)
		else:
			self.numSuccesses += 1
			self.lastSuccess = today
			self.setNextReview(reverse)
	
	def setState(self, state, reverse):
		if reverse:
			self.reverseState = state
		else:
			self.state = state
		if state == 'missed':
			self.updateMisses(reverse)
		else:
			self.updateSuccesses(reverse)
	
	def setNextReview(self, reverse):
		n = 0
		if reverse:
			n = self.reverseNumSuccesses
		else:
			n = self.numSuccesses
		delta = pow(1.1, n)
		if delta < 1:
			delta = 1
		elif delta > 500:
			delta = 500
		if reverse:
			self.nextReverseReviewDate = self.lastReverseSuccess + datetime.timedelta(days=(int(delta)))
		else:
			self.nextReviewDate = self.lastSuccess + datetime.timedelta(days=(int(delta)))
