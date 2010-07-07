from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import datetime

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

class NewPairForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
	
		category_key = self.request.get('category')
		path = os.path.join(os.path.dirname(__file__), 'templates/new_pair.html')
		self.response.out.write(template.render(path, {'category_key': category_key,
														'logout': logout}))

class AddPairAction(webapp.RequestHandler):
	def post(self):
		category_key = self.request.get('category')
		pair = Pair(owner = users.get_current_user())
		pair.question = self.request.get('question')
		pair.answer = self.request.get('answer')
		pair.categories.append(db.Key(category_key))
		pair.put()
		category = db.get(category_key)
		category.total += 1
		category.remaining += 1
		category.put()
		self.redirect('/category?id=' + category_key)

class UpdatePairAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		state = self.request.get('state')
		category_key = self.request.get('category')
		pair = db.get(pair_key)		
		
		#update category meta information
		category = db.get(category_key)
		pair.setState(state, category.reviewing)
		if state == 'missed':
			category.addMissed(1)
		elif state == 'correct':
			if category.reviewing:
				pair.numSuccesses += 1
				pair.lastSuccess = datetime.date.today()
				pair.reviewFrequency = calculateReviewFrequency(pair)
			category.addCorrect(1)
		else:
			category.addError(1)
		category.addRemaining(-1)	
		pair.put()
		category.put()
		self.redirect('/category?id=' + category_key)

class MarkReviewAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		category_key = self.request.get('category')
		pair = db.get(pair_key)
		pair.reviewing = True
		pair.firstSuccess = datetime.date.today()
		pair.lastSuccess = pair.firstSuccess
		pair.numSuccesses = 1
		pair.reviewFrequency = 'daily'
		pair.state = 'correct'
		pair.put()
		category = db.get(category_key)
		category.correct += 1
		category.remaining -= 1
		category.put()
		self.redirect('/category?id=' + category_key)

def calculateReviewFrequency(pair):
	n = pair.numSuccesses
	f = ''
	if n < 8:
		f = 'daily'
	elif n < 12:
		f = 'weekly'
	elif n < 25:
		f = 'monthly'
	else:
		f = 'yearly'
	return f

#hack to fix circular import
from category import *
