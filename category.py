from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import random
import datetime

from pair import *

class Category(db.Model):
	name = db.StringProperty()
	owner = db.UserProperty(required = True)
	description = db.TextProperty()
	
	# Category meta information
	size = db.IntegerProperty(default=0)
	total = db.IntegerProperty(default=0)
	missed = db.IntegerProperty(default=0)
	correct = db.IntegerProperty(default=0)
	remaining = db.IntegerProperty(default=0)
	error = db.IntegerProperty(default = 0)
	
	reviewing = db.BooleanProperty(default=False)
	
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
	
	@property
	def allReviewPairs(self):
		pairs = self.dailyReviewPairs + \
				self.weeklyReviewPairs + \
				self.monthlyReviewPairs + \
				self.yearlyReviewPairs
		return pairs
	
	@property
	def readyReviewPairs(self):
		allPairs = self.allReviewPairs
		pairs = filter(lambda p: p.state == 'ready')
		return pairs
	
	@property
	def missedReviewPairs(self):
		allPairs = self.allReviewPairs
		pairs = filter(lambda p: p.state == 'missed')
		return pairs
	
	@property
	def correctReviewPairs(self):
		allPairs = self.allReviewPairs
		pairs = filter(lambda p: p.state == 'correct')
		return pairs
	
	@property
	def dailyReviewPairs(self):
		date = datetime.today() - datetime.timedelta(1)
		pairs = self.reviewPairs(8, date)
		return pairs
	
	@property
	def weeklyReviewPairs(self):
		date = datetime.today() - datetime.timedelta(7)
		pairs = self.reviewPairs(12, date)
		return pairs
	
	@property
	def monthlyReviewPairs(self):
		date = datetime.today() - datetime.timedelta(30)
		pairs = self.reviewPairs(25, date)
		return pairs
	
	@property
	def yearlyReviewPairs(self):
		date = datetime.today() - datetime.timedelta(365)
		pairs = self.reviewPairs(None, date)
		return pairs
	
	@property
	def reviewPairs(self, numSuccesses, date):
		query = Pair.all().filter('categories =', self.key())
		if numSuccesses:
			query.filter('numSuccesses <', numSuccesses)
		query.filter('lastSuccess <=', date)
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
		if not category:
			error_message = "Category does not exist"
		elif category.owner != user:
			error_message = "You do not own this category"
		else:
			if pairKey:
				pair = db.get(pairKey)
			else:
				if category.reviewing:
					pairs = category.readyReviewPairs
				else:
					pairs = category.readyPairs
				if len(pairs) == 0:
					reset_pairs(category_key)
					pairs = category.readyPairs
					
					# get updated meta information
					category = db.get(category_key)
					
				#make sure there are pairs in the category (avoid out of bounds error)	
				if len(pairs) > 0:
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

class SetReviewingAction(webapp.RequestHandler):
	def post(self):
		category_key = self.request.get('category')
		category = db.get(category_key)
		category.reviewing = True
		category.put()
		self.redirect('/category?id=' + category_key)

def reset_pairs(categoryKey):
	category = db.get(categoryKey)
	pairs = category.missedPairs
	changed = False
	category.remaining = 0
	while len(pairs) > 0:
		changed = True
		category.remaining += len(pairs)
		for pair in pairs:
			pair.state = 'ready'
			pair.put()
		pairs = category.missedPairs
	if changed:
		category.missed = 0
		category.put()
	else:
		pairs = category.correctPairs
		while len(pairs) > 0:
			changed = True
			category.remaining += len(pairs)
			for pair in pairs:
				pair.state = 'ready'
				pair.put()
			pairs = category.correctPairs
		category.correct = 0
		category.put()
