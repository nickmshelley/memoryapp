from google.appengine.ext import db
from google.appengine.api import memcache
import datetime
import random
from models.pairModel import *
from models.userPreferencesModel import *

class Category(db.Model):	
	name = db.StringProperty()
	owner = db.UserProperty(required = True)
	description = db.TextProperty()
	reverse = db.BooleanProperty()
	
	def getReviewPairsKey(self):
		return str(self.key()) + "reviewPairs"
	
	def getAllFromQuery(self, query):
		items = []
		for item in query:
			items.append(item)
		return items
	
	@property
	def allPairs(self):
		query = Pair.all().filter('categories =', self.key())
		pairs = self.getAllFromQuery(query)
		return pairs
	
	@property
	def reviewPairs(self):
		pairs = self.getReviewPairs()
		return pairs
	
	#tells how many cards still need review
	@property
	def remaining(self):
		return len(self.reviewPairs)

	@property
	def nextPair(self):
		pairs = self.reviewPairs
		if len(pairs) == 0:
			pair = None
		else:
			index = int(pow(random.random(), 2) * len(pairs))
			#print index
			pair = pairs[index]
		return pair
	
	def getReviewPairs(self):
		key = self.getReviewPairsKey()
		pairs = memcache.get(key)
		if pairs is None:
			prefs = UserPreferences.getUserPreferences()
			offset = prefs.timeOffset
			now = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
			date = now.date() # get rid of time information
			
			query = Pair.all().filter('categories =', self.key())
			if self.reverse:
				query.filter('nextReverseReviewDate <=', date)
			else:
				query.filter('nextReviewDate <=', date)
			pairs = self.getAllFromQuery(query)
			
			#sort by numsuccesses minus how-many-days-past-review-date
			def compare(pair):
				num = 0
				if self.reverse:
					dayDiff = 0
					if pair.lastReverseSuccess is not None:
						dayDiff = (pair.nextReverseReviewDate - pair.lastReverseSuccess).days
					num = (pair.reverseNumSuccesses + dayDiff - (date - pair.nextReverseReviewDate).days)
					if pair.reverseState == 'missed':
						num -= 1000
				else:
					dayDiff = 0
					if pair.lastSuccess is not None:
						dayDiff = (pair.nextReviewDate - pair.lastSuccess).days
					num = (pair.numSuccesses + dayDiff - (date - pair.nextReviewDate).days)
					if pair.state == 'missed':
						num -= 1000
				return num
			pairs.sort(key = compare)
			
			#algorithm works better with fewer pairs
			pairs = pairs[:200]
			memcache.set(key, pairs)
		return pairs
