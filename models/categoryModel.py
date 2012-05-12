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
			query.filter('nextReviewDate <=', date)
			pairs = self.getAllFromQuery(query)
			
			#sort by numsuccesses minus how-many-days-past-review-date
			def compare(pair):
				num = (pair.numSuccesses - (date - pair.nextReviewDate).days)
				if pair.state == 'missed':
					num -= 1000
				return num
			pairs.sort(key = compare)
			
			#for pair in pairs:
			#	print "%s-%d" % (pair.state, (pair.numSuccesses - (date - pair.nextReviewDate).days))
			
			memcache.set(key, pairs[:500])
		return pairs
