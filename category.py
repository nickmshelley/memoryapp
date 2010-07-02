from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import random

from pair import *

class Category(db.Model):
	name = db.StringProperty()
	owner = db.UserProperty(required = True)
	description = db.TextProperty()
	
	# Category meta information
	size = db.IntegerProperty(default=0)
	missed = db.IntegerProperty(default=0)
	correct = db.IntegerProperty(default=0)
	remaining = db.IntegerProperty(default=0)
	error = db.IntegerProperty(default = 0)
	
	@property
	def allPairs(self):
		query = Pair.all().filter('categories =', self.key())
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def readyPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'ready')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def missedPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'missed')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def correctPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'correct')
		pairs = query.fetch(1000)
		return pairs

class CategoryPage(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
	
		user = users.get_current_user()
		category_key = self.request.get('id')
		pairKey = self.request.get('pair')
		showAnswer = self.request.get('show-answer')
		category = db.get(category_key)
		error_message = None
		path = os.path.join(os.path.dirname(__file__), 'templates/category.html')
		pairs = []
		pair = None
		changed = True
		if not category:
			error_message = "Category does not exist"
		elif category.owner != user:
			error_message = "You do not own this category"
		else:
			if pairKey:
				pair = db.get(pairKey)
			else:
				pairs = category.readyPairs
				if len(pairs) == 0:
					changed = reset_pairs(category)
					
				#make sure there are pairs in the category (avoid out of bounds error)	
				if changed:
					pairs = category.readyPairs
					index = random.randint(0, len(pairs) - 1)
					pair = pairs[index]
			
		self.response.out.write(template.render(path, {'pair': pair,
														'category': category,
														'show_answer': showAnswer,
														'logout': logout,
														'error_message': error_message,
														}))

class NewCategoryForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		path = os.path.join(os.path.dirname(__file__), 'templates/new_category.html')
		self.response.out.write(template.render(path, {'logout': logout}))

class AddCategoryAction(webapp.RequestHandler):
	def post(self):
		category = Category(owner = users.get_current_user())
		name = self.request.get('name')
		if len(name) == 0:
			name = "Untitled Category"
		category.name = name
		category.description = self.request.get('description')
		category.put()
		self.redirect('/')

def reset_pairs(category):
	changed = reset_missed(category)
	if not changed:
		changed = reset_correct(category)
	return changed

def reset_missed(category):
	pairs = []
# 	if category.reviewing:
# 		pairs = category.missedReviewPairs
# 	else:
# 		pairs = category.missedPairs
	pairs = category.missedPairs
	category.remaining = 0
	changed = False
	while len(pairs) > 0:
		changed = True
		category.remaining += len(pairs)
		for pair in pairs:
			pair.state = 'ready'
			pair.put()
# 		if category.reviewing:
# 			pairs = cagegory.missedReviewPairs
# 		else:
# 			pairs = category.missedPairs
		pairs = category.missedPairs
	if changed:
		category.missed = 0
		category.put()
	return changed

def reset_correct(category):
	pairs = []
	#don't need to do this for review because if all are correct, it exits the review
	pairs = category.correctPairs
	changed = False
	while len(pairs) > 0:
		changed = True
		category.remaining += len(pairs)
		for pair in pairs:
			pair.state = 'ready'
			pair.put()
		pairs = category.correctPairs
	if changed:
		category.correct = 0
		category.put()
	return changed
		
