from google.appengine.ext import db

class Pair(db.Model):
	owner = db.UserProperty(required = True)
	
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
	
	def setState(self, state, reviewing):
		if reviewing:
			self.reviewState = state
		else:
			self.state = state