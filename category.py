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
	total = db.IntegerProperty(default=0)
	missed = db.IntegerProperty(default=0)
	correct = db.IntegerProperty(default=0)
	remaining = db.IntegerProperty(default=0)
	reviewTotal = db.IntegerProperty(default=0)
	reviewMissed = db.IntegerProperty(default=0)
	reviewCorrect = db.IntegerProperty(default=0)
	reviewRemaining = db.IntegerProperty(default=0)
	error = db.IntegerProperty(default = 0)
	
	reviewing = db.BooleanProperty(default=False)
	
	def setMissed(self, num):
		if self.reviewing:
			self.reviewMissed = num
		else:
			self.missed = num
	
	def addMissed(self, num):
		if self.reviewing:
			self.reviewMissed += num
		else:
			self.missed += num
	
	def setRemaining(self, num):
		if self.reviewing:
			self.reviewRemaining = num
		else:
			self.remaining = num
	
	def addRemaining(self, num):
		if self.reviewing:
			self.reviewRemaining += num
		else:
			self.remaining += num
	
	def setCorrect(self, num):
		if self.reviewing:
			self.reviewCorrect = num
		else:
			self.correct = num
	
	def addCorrect(self, num):
		if self.reviewing:
			self.reviewCorrect += num
		else:
			self.correct += num
	
	def getCounts(self):
		if self.reviewing:
			return self.getReviewCounts()
		else:
			return self.getAllCounts()
	
	def getAllCounts(self):
		counts = {
				'total': self.total,
				'missed': self.missed,
				'correct': self.correct,
				'remaining': self.remaining,
				}
		return counts
	
	def getReviewCounts(self):
		counts = {
				'total': self.reviewTotal,
				'missed': self.reviewMissed,
				'correct': self.reviewCorrect,
				'remaining': self.reviewRemaining,
				}
		return counts
	
	@property
	def pairs(self):
		if self.reviewing:
			return self.reviewPairs
		else:
			return self.allPairs
	
	@property
	def allPairs(self):
		query = Pair.all().filter('categories =', self.key())
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewPairs(self):
		pairs = self.dailyReviewPairs + \
				self.weeklyReviewPairs + \
				self.monthlyReviewPairs + \
				self.yearlyReviewPairs
		return pairs
	
	@property
	def readyPairs(self):
		if self.reviewing:
			return self.reviewReadyPairs
		else:
			return self.allReadyPairs
	
	@property
	def allReadyPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'ready')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewReadyPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'ready']
		#pairs = filter(lambda p: p.state == 'ready', allPairs)
		return pairs
	
	@property
	def missedPairs(self):
		if self.reviewing:
			return self.reviewMissedPairs
		else:
			return self.allMissedPairs
	
	@property
	def allMissedPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'missed')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewMissedPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'missed']
		#pairs = filter(lambda p: p.state == 'missed', allPairs)
		return pairs
	
	@property
	def correctPairs(self):
		if self.reviewing:
			return self.reviewCorrectPairs
		else:
			return self.allCorrectPairs
	
	@property
	def allCorrectPairs(self):
		query = Pair.all().filter('categories =', self.key())
		query.filter('state =', 'correct')
		pairs = query.fetch(1000)
		return pairs
	
	@property
	def reviewCorrectPairs(self):
		allPairs = self.reviewPairs
		pairs = [p for p in allPairs if p.reviewState == 'correct']
		#pairs = filter(lambda p: p.state == 'correct', allPairs)
		return pairs
	
	@property
	def dailyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(1)
		pairs = self.getReviewPairs('daily', date)
		return pairs
	
	@property
	def weeklyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(7)
		pairs = self.getReviewPairs('weekly', date)
		return pairs
	
	@property
	def monthlyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(30)
		pairs = self.getReviewPairs('monthly', date)
		return pairs
	
	@property
	def yearlyReviewPairs(self):
		date = datetime.date.today() - datetime.timedelta(365)
		pairs = self.getReviewPairs('yearly', date)
		return pairs
	
	def getReviewPairs(self, frequency, date):
		query = Pair.all().filter('categories =', self.key())
		query.filter('reviewFrequency =', frequency)
		#query.filter('lastSuccess <=', date)
		pairs = query.fetch(1000)
		return pairs
	

class CategoryPage(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		
		counts = None
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
					changed = reset_pairs(category, self)
					
				#make sure there are pairs in the category (avoid out of bounds error)	
				if changed:
					pairs = category.readyPairs
					index = random.randint(0, len(pairs) - 1)
					pair = pairs[index]
			counts = category.getCounts()
			
		self.response.out.write(template.render(path, {'pair': pair,
														'category_key': category_key,
														'reviewing': category.reviewing,
														'counts': counts,
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
		reviewing = self.request.get('reviewing')
		category = db.get(category_key)
		if reviewing == 'True':
			category.reviewing = False
			category.put()
		else:
			pairs = category.reviewPairs
			size = len(pairs)
			if size > 0:
				reset_missed(category)
				reset_correct(category)
				category.reviewTotal = size
				category.reviewRemaining = size
				category.reviewing = True
				category.put()
		self.redirect('/category?id=' + category_key)

def reset_pairs(category, handler):
	changed = reset_missed(category)
	if not changed:
		changed = reset_correct(category)
		if category.reviewing:
			category.reviewing = False
			category.put()
			handler.redirect('/category?id=' + str(category.key()))
	return changed

def reset_missed(category):
	pairs = []
	pairs = category.missedPairs
	category.setRemaining(0)
	changed = False
	while len(pairs) > 0:
		changed = True
		category.addRemaining(len(pairs))
		for pair in pairs:
			pair.setState('ready', category.reviewing)
			pair.put()
		pairs = category.missedPairs
	if changed:
		category.setMissed(0)
		category.put()
	return changed

def reset_correct(category):
	pairs = []
	pairs = category.correctPairs
	changed = False
	while len(pairs) > 0:
		changed = True
		category.addRemaining(len(pairs))
		for pair in pairs:
			pair.setState('ready', category.reviewing)
			pair.put()
		pairs = category.correctPairs
	if changed:
		category.setCorrect(0)
		category.put()
	return changed
		
