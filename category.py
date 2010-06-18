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
	size = db.IntegerProperty()
	missed = db.IntegerProperty()
	correct = db.IntegerProperty()
	
	@property
	def pairs(self):
		return Pair.all().filter('categories =', self.key())

class CategoryPage(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
	
		user = users.get_current_user()
		categoryKey = self.request.get('id')
		pairKey = self.request.get('pair')
		showAnswer = self.request.get('show-answer')
		category = db.get(categoryKey)
		error_message = None
		path = os.path.join(os.path.dirname(__file__), 'templates/category.html')
		pairs = []
		pair = None
		if not category:
			error_message = "Category does not exist"
		elif category.owner != user:
			error_message = "You do not own this category"
		else:
			pairsQuery = category.pairs
			pairsQuery.filter('state =', 'ready')
			if pairKey:
				pair = db.get(pairKey)
			else:
				pairs = pairsQuery.fetch(1000)
				if len(pairs) == 0:
					reset_pairs(categoryKey)
					pairs = pairsQuery.fetch(1000)
				if len(pairs) > 0:
					index = random.randint(0, len(pairs) - 1)
					pair = pairs[index]
			
		self.response.out.write(template.render(path, {'pair': pair,
														'category_key': categoryKey,
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

def reset_pairs(categoryKey):
	category = db.get(categoryKey)
	pairsQuery = category.pairs.filter('state =', 'missed')
	pairs = pairsQuery.fetch(1000)
	changed = False
	while len(pairs) > 0:
		changed = True
		for pair in pairs:
			pair.state = 'ready'
			pair.put()
		pairs = pairsQuery.fetch(1000)
	if not changed:
		pairsQuery = category.pairs.filter('state =', 'correct')
		pairs = pairsQuery.fetch(1000)
		while len(pairs) > 0:
			changed = True
			for pair in pairs:
				pair.state = 'ready'
				pair.put()
			pairs = pairsQuery.fetch(1000)
