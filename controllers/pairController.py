from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from models.userPreferencesModel import UserPreferences
import os
import datetime
import random

class NewPairForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
	
		category_key = self.request.get('category')
		path = os.path.join(os.path.dirname(__file__), '../templates/new_pair.html')
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
		self.redirect('/category?id=' + category_key  + ';pair=' + str(pair.key()))

class EditPairForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		category_key = self.request.get('category')
		pair_key = self.request.get('pair')
		pair = db.get(pair_key)
		question = pair.question
		answer = pair.answer
		path = os.path.join(os.path.dirname(__file__), '../templates/edit_pair.html')
		self.response.out.write(template.render(path, {'category_key': category_key,
														'pair_key': pair_key,
														'question': question,
														'answer': answer,
														'logout': logout,
														}))

class EditPairAction(webapp.RequestHandler):
	def post(self):
		category_key = self.request.get('category')
		pair_key = self.request.get('id')
		pair = db.get(pair_key)
		pair.question = self.request.get('question')
		pair.answer = self.request.get('answer')
		pair.updateDbAndCache()
		self.redirect('/category?id=' + category_key + ';pair=' + pair_key)

class DeletePair(webapp.RequestHandler):
	def get(self):
		category_key = self.request.get('category')
		category = Category.get(category_key)
		pair_key = self.request.get('pair')
		pair = Pair.get(pair_key)
		category.deletePair(pair)
		category.put()
		logout = users.create_logout_url(self.request.uri)
		self.redirect('/category?id=' + category_key)

class UpdatePairAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		state = self.request.get('state')
		category_key = self.request.get('category')
		category = db.get(category_key)
		pair = db.get(pair_key)
		
		# update random ordering number if not reviewing
		if not category.reviewing:
			pair.order = random.randint(1, 99999)
		
		#update category meta information
		pair.setState(state, category.reviewing)
		if state == 'missed':
			if category.reviewing:
				pair.updateMisses()
			category.addMissed(1)
		elif state == 'correct':
			if category.reviewing:
				pair.updateSuccesses()
			category.addCorrect(1)
			category.addReviewed(1)
		else:
			category.error += 1
		category.addRemaining(-1)	
		pair.updateDbAndCache()
		category.put()
		self.redirect('/category?id=' + category_key)

class MarkReviewAction(webapp.RequestHandler):
	def post(self):
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		today = now.date() # get rid of time information
		pair_key = self.request.get('pair')
		category_key = self.request.get('category')
		pair = db.get(pair_key)
		pair.reviewing = True
		pair.firstSuccess = today
		pair.lastSuccess = pair.firstSuccess
		pair.numSuccesses = 1
		pair.setNextReview();
		pair.put()
		self.redirect('/category?id=' + category_key + '&pair=' + pair_key)

#hack to fix circular import
from models.categoryModel import *
