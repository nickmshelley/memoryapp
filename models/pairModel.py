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
	state = db.CategoryProperty(default = 'ready') #missed, correct, ready, etc.
	reviewState = db.CategoryProperty(default = 'ready') #same as above but used in review mode
	reviewing = db.BooleanProperty(default = False)
	numSuccesses = db.IntegerProperty(default = 0)
	
	# Date info
	firstSuccess = db.DateProperty()
	lastSuccess = db.DateProperty()
	nextReviewDate = db.DateProperty()
	
	# Category Affiliation
	categories = db.ListProperty(db.Key)
	
	def updateDbAndCache(self):
		self.put()
		for category_key in self.categories:
			key = str(category_key) + "reviewPairs"
			pairs = memcache.get(key)
			if pairs is not None:
				tempPairs = [p for p in pairs if str(self.key()) == str(p.key())]
				if len(tempPairs) > 1:
					print "logic error"
				try:
					pairs.remove(tempPairs[0])
					pairs.append(self)
					memcache.set(key, pairs)
				except:
					pass
	
	def updateMisses(self):
		self.numSuccesses -= 2;
		if self.numSuccesses < 0:
			self.numSuccesses = 0
	
	def updateSuccesses(self):
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		
		now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		today = now.date() # get rid of time information
		self.numSuccesses += 1
		self.lastSuccess = today
		self.setNextReview()
	
	def setState(self, state, reviewing):
		if reviewing:
			self.reviewState = state
		else:
			self.state = state
	
	def setNextReview(self):
		n = self.numSuccesses
		delta = pow(1.1, n)
		if delta < 1:
			delta = 1
		elif delta > 500:
			delta = 500
		self.nextReviewDate = self.lastSuccess + datetime.timedelta(days=(int(delta)))