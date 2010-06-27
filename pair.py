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
	state = db.CategoryProperty() #missed, correct, ready, etc.
	reviewing = db.BooleanProperty()
	numSuccesses = db.IntegerProperty()
	
	# Date info
	firstSuccess = db.DateProperty()
	lastSuccess = db.DateProperty()
	
	# Category Affiliation
	categories = db.ListProperty(db.Key)

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
		pair.state = db.Category("ready")
		pair.categories.append(db.Key(category_key))
		pair.put()
		category = db.get(category_key)
		category.size += 1
		category.remaining += 1
		category.put()
		self.redirect('/category?id=' + category_key)

class UpdatePairAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		state = self.request.get('state')
		category_key = self.request.get('category')
		pair = db.get(pair_key)		
		pair.state = state
		pair.put()
		
		#update category meta information
		category = db.get(category_key)
		if state == 'missed':
			category.missed += 1
		elif state == 'correct':
			category.correct += 1
		else:
			category.error += 1
		category.remaining -= 1	
		category.put()
		self.redirect('/category?id=' + category_key)

class MarkReviewAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		category_key = self.request.get('category')
		pair = db.get(pair_key)
		pair.reviewing = True
		pair.firstSuccess = datetime.date.today()
		pair.numSuccesses = 1
		pair.state = 'correct'
		pair.put()
		category = db.get(category_key)
		category.correct += 1
		category.remaining -= 1
		category.put()
		self.redirect('/category?id=' + category_key)

#hack to fix circular import
from category import *
