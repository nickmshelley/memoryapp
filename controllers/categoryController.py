from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.api import memcache
import os
import random
from models.categoryModel import *

class CategoryPage(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		
		counts = None
		user = users.get_current_user()
		category_key = self.request.get('id')
		pairKey = self.request.get('pair')
		showAnswer = self.request.get('show-answer')
		error_message = None
		category = None
		reviewing = None
		try:
			category = db.get(category_key)
		except db.BadKeyError:
			error_message = "Category does not exist"
		else:
			reviewing = category.reviewing
			counts = category.getCounts()
		path = os.path.join(os.path.dirname(__file__), '../templates/category.html')
		pair = None
		doneReviewing = False
		if not category:
			pass
		elif category.owner != user:
			error_message = "You do not own this category"
		elif category.total > 0:
			if pairKey:
				pair = db.get(pairKey)
			else:
				pair = category.nextPair
				if pair is None:
					doneReviewing = category.resetPairs()
					category.put()
					if doneReviewing:
						self.redirect('/category?id=' + str(category.key()))
				pair = category.nextPair
				if pair is None:
					print "*********ERROR##########"
				counts = category.getCounts()
			
		self.response.out.write(template.render(path, {'pair': pair,
														'category': category,
														'reviewing': reviewing,
														'counts': counts,
														'show_answer': showAnswer,
														'logout': logout,
														'error_message': error_message,
														}))

class NewCategoryForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		path = os.path.join(os.path.dirname(__file__), '../templates/new_category.html')
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

class EditCategoryForm(webapp.RequestHandler):
	def get(self):
		key = self.request.get('id')
		category = db.get(key)
		name = category.name
		description = category.description
		logout = users.create_logout_url(self.request.uri)
		path = os.path.join(os.path.dirname(__file__), '../templates/edit_category.html')
		self.response.out.write(template.render(path, {'logout': logout, 
														'name': name,
														'description': description,
														'category_key': key,
														}))

class EditCategoryAction(webapp.RequestHandler):
	def post(self):
		key = self.request.get('id')
		category = db.get(key)
		name = self.request.get('name')
		if len(name) == 0:
			name = "Untitled Category"
		category.name = name
		category.description = self.request.get('description')
		category.put()
		self.redirect('/')

class DeleteCategory(webapp.RequestHandler):
	def get(self):
		key = self.request.get('category')
		category = Category.get(key)
		pairs = category.allPairs
		step = 200
		length = len(pairs)
		# delete pairs in chunks of 200 because of GAE time and quantity restrictions
		for i in range(0, length, step):
			lower = i
			upper = i + step
			if upper > length:
				upper = length
			db.delete(pairs[lower:upper])
		db.delete(category)
		self.redirect('/')

class ViewPairs(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		key = self.request.get('category')
		page = self.request.get('page')
		category = Category.get(key)
		pairQuery = Pair.all().filter('categories =', category.key())
		pairQuery.order('reviewing')
		pairQuery.order('nextReviewDate')
		pairQuery.order('numSuccesses')
		if page == 'next':
			lastCursor = memcache.get('card_cursor')
			if lastCursor:
				pairQuery.with_cursor(lastCursor)
		pairs = pairQuery.fetch(100)
		cursor = pairQuery.cursor()
		memcache.set('card_cursor', cursor)
		path = os.path.join(os.path.dirname(__file__), '../templates/view_pairs.html')
		self.response.out.write(template.render(path, {'logout': logout,
														'pairs': pairs,
														'category': category,
														}))

class ViewStats(webapp.RequestHandler):
	def get(self):
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		today = now.date() # get rid of time information
		logout = users.create_logout_url(self.request.uri)
		key = self.request.get('category')
		category = Category.get(key)
		pairs = category.allPairs
		reviewLevel = {}
		days = {}
		averages = {}
		for n in range(max(pairs, key=lambda x: x.numSuccesses).numSuccesses + 1):
			reviewLevel[n] = filter(lambda x: x.numSuccesses == n, pairs)
		reviewLevelList = []
		total = 0
		for n in reviewLevel.keys():
			#review level stuff
			l = reviewLevel[n]
			num = len(l)
			reviewLevelList.append((n, num, 
									len(filter(lambda x: x.nextReviewDate <= today, l)),
									len(filter(lambda x: x.nextReviewDate > today, l))))
			total += num * n
			#days stuff
			delta = int(pow(1.1, n))
			if not delta in days:
				days[delta] = num
			else:
				days[delta] += num
		averages['reviewLevel'] = total / len(pairs)
		averages['days'] = sum(days.values())
		numCards = 0.0
		for n in days.keys():
			numCards += days[n] / float(n)
		averages['cards'] = numCards
		path = os.path.join(os.path.dirname(__file__), '../templates/view_stats.html')
		self.response.out.write(template.render(path, {'logout': logout,
														'reviewLevel': reviewLevelList,
														'days': days,
														'averages': averages,
														'category': category,
														}))

class SetReviewingAction(webapp.RequestHandler):
	def post(self):
		category_key = self.request.get('category')
		reviewing = self.request.get('reviewing')
		category = db.get(category_key)
		if reviewing == 'True':
			category.unsetReviewing()
			category.put()
		else:
			category.setReviewing()
			category.reviewedThisSession = 0
			pairs = category.reviewPairs
			size = len(pairs)
			if size > 0:
				category.resetMissed()
				category.resetCorrect()
				category.reviewTotal = size
				category.reviewRemaining = size
				category.reviewMissed = 0
				category.reviewCorrect = 0
				category.put()
			else:
				category.unsetReviewing()
		self.redirect('/category?id=' + category_key)
