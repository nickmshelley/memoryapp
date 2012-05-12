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
	
	# Date info
	firstSuccess = db.DateProperty()
	lastSuccess = db.DateProperty()
	nextReviewDate = db.DateProperty()
	
	# Category Affiliation
	categories = db.ListProperty(db.Key)
	
	def updateDbAndCache(self, category_key):
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
				if self.state == 'missed':
					self.insertAfterMissed(pairs)
				memcache.set(key, pairs)
			except:
				pass
	
	def insertAfterMissed(self, pairs):
		for i in range(length(pairs)):
			if pairs.state == 'ready':
				pairs.insert(i, self)
				break
	
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
	
	def setState(self, state):
		self.state = state
		if state == 'missed':
			self.updateMisses()
		else:
			self.updateSuccesses()
	
	def setNextReview(self):
		n = self.numSuccesses
		delta = pow(1.1, n)
		if delta < 1:
			delta = 1
		elif delta > 500:
			delta = 500
		self.nextReviewDate = self.lastSuccess + datetime.timedelta(days=(int(delta)))