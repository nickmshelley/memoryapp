from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import random
from categoryModel import *

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
		path = os.path.join(os.path.dirname(__file__), 'templates/category.html')
		pairs = []
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
				pairs = category.readyPairs
				if len(pairs) == 0:
					doneReviewing = category.resetPairs()
					category.put()
					if doneReviewing:
						self.redirect('/category?id=' + str(category.key()))
				pairs = category.readyPairs
				index = random.randint(0, len(pairs) - 1)
				pair = pairs[index]
				counts = category.getCounts()
			
		self.response.out.write(template.render(path, {'pair': pair,
														'category_key': category_key,
														'reviewing': reviewing,
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
			category.unsetReviewing()
			category.put()
		else:
			pairs = category.reviewPairs
			size = len(pairs)
			if size > 0:
				category.setReviewing()
				category.resetMissed()
				category.resetCorrect()
				category.reviewTotal = size
				category.reviewRemaining = size
				category.put()
		self.redirect('/category?id=' + category_key)
