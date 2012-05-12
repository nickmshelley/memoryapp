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
		
		user = users.get_current_user()
		category_key = self.request.get('id')
		pairKey = self.request.get('pair')
		showAnswer = self.request.get('show-answer')
		error_message = None
		category = None
		category = db.get(category_key)
		path = os.path.join(os.path.dirname(__file__), '../templates/category.html')
		pair = None
		if pairKey:
			pair = db.get(pairKey)
		else:
			pair = category.nextPair
		if pair is None:
			self.redirect('/view-stats?category=' + str(category.key()))
		remaining = category.remaining
		self.response.out.write(template.render(path, {'pair': pair,
														'category': category,
														'remaining': remaining,
														'show_answer': showAnswer,
														'logout': logout,
														}))

class StartReviewAction(webapp.RequestHandler):
	def get(self):
		category_key = self.request.get('id')
		category = db.get(category_key)
		memcache.delete(category.getReviewPairsKey())
		self.redirect('category?id=' + category_key)

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
		total = len(pairs)
		reviewTotal = len(filter(lambda x: x.nextReviewDate <= today, pairs))
		totals = {'total': total, 'reviewTotal': reviewTotal}
		reviewLevel = {}
		days = {}
		averages = {}
		reviewLevelList = []
		if len(pairs) > 0:
			for n in range(max(pairs, key=lambda x: x.numSuccesses).numSuccesses + 1):
				reviewLevel[n] = filter(lambda x: x.numSuccesses == n, pairs)
			dayAveTotal = 0
			daysTotal = 0.0
			for n in reviewLevel.keys():
				#review level stuff
				l = reviewLevel[n]
				num = len(l)
				reviewLevelList.append((n, num, 
										len(filter(lambda x: x.nextReviewDate <= today, l)),
										len(filter(lambda x: x.nextReviewDate > today, l))))
				dayAveTotal += num * n
				#days stuff
				delta = int(pow(1.1, n))
				if not delta in days:
					days[delta] = num
				else:
					days[delta] += num
				daysTotal += delta * float(num)
			averages['reviewLevel'] = dayAveTotal / float(total)
			averages['days'] = daysTotal / float(total)
			numCards = 0.0
			for n in days.keys():
				numCards += days[n] / float(n)
			averages['cards'] = numCards
		path = os.path.join(os.path.dirname(__file__), '../templates/view_stats.html')
		self.response.out.write(template.render(path, {'logout': logout,
														'totals': totals,
														'reviewLevel': reviewLevelList,
														'days': days,
														'averages': averages,
														'category': category,
														}))
