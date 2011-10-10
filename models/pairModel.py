from google.appengine.ext import db
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
	
	def updateMisses(self):
		self.numSuccesses -= 1;
	
	def updateSuccesses(self):
		prefs = UserPreferences.all().filter('user =', users.get_current_user()).fetch(1)[0]
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
		delta = pow(1.2, n)
		if delta > 500:
			delta = 500
		self.nextReviewDate = self.lastSuccess + datetime.timedelta(days=(int(delta)))