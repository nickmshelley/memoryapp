from google.appengine.ext import db
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
	reviewFrequency = db.CategoryProperty() #daily, weekly, monthly, yearly
	
	# Category Affiliation
	categories = db.ListProperty(db.Key)
	
	def updateSuccesses(self):
		now = datetime.datetime.now() - datetime.timedelta(hours=8) # adjust for utc time
		today = now.date() # get rid of time information
		self.numSuccesses += 1
		self.lastSuccess = today
		self.setReviewFrequency()
	
	def setState(self, state, reviewing):
		if reviewing:
			self.reviewState = state
		else:
			self.state = state
	
	def setReviewFrequency(self):
		n = self.numSuccesses
		f = ''
		if n < 8:
			f = 'daily'
		elif n < 12:
			f = 'weekly'
		elif n < 25:
			f = 'monthly'
		else:
			f = 'yearly'
		self.reviewFrequency = f