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
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		today = now.date() # get rid of time information
		category_key = self.request.get('category')
		pair = Pair(owner = users.get_current_user())
		pair.question = self.request.get('question')
		pair.answer = self.request.get('answer')
		pair.nextReviewDate = today
		pair.categories.append(db.Key(category_key))
		pair.put()
		self.redirect('/view-stats?category=' + category_key)

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
		pair.updateDbAndCache(category_key)
		#refresh cache to show update
		category = db.get(category_key)
		memcache.delete(category.getReviewPairsKey())
		self.redirect('/category?id=' + category_key + ';pair=' + pair_key)

class DeletePair(webapp.RequestHandler):
	def get(self):
		pair_key = self.request.get('pair')
		pair = Pair.get(pair_key)
		pair.delete()
		logout = users.create_logout_url(self.request.uri)
		self.redirect('/category?id=' + category_key)

class UpdatePairAction(webapp.RequestHandler):
	def post(self):
		pair_key = self.request.get('pair')
		state = self.request.get('state')
		category_key = self.request.get('category')
		pair = db.get(pair_key)
		
		pair.setState(state)
		pair.updateDbAndCache(category_key)
		self.redirect('/category?id=' + category_key)

#hack to fix circular import
from models.categoryModel import *
