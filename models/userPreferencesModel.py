from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

class UserPreferences(db.Model):
	user = db.UserProperty(required = True)
	
	# offset in hours from UTC time
	# this number is subtracted from UTC time, so should be positive if going west
	timeOffset = db.IntegerProperty(default = 8)
	
	@staticmethod
	def getMemcacheKey():
		return str(users.get_current_user()) + "userPrefs"
	
	def updateDbAndCache(self):
		self.put()
		key = self.getMemcacheKey()
		memcache.set(key, self)
	
	@staticmethod
	def getUserPreferences():
		user = users.get_current_user()
		key = UserPreferences.getMemcacheKey()
		prefs = memcache.get(key)
		if prefs is None:
			prefs = UserPreferences.all().filter('user =', user).fetch(1)[0]
			memcache.set(key, prefs)
		return prefs