from google.appengine.ext import db
import datetime

class UserPreferences(db.Model):
	user = db.UserProperty(required = True)
	
	# offset in hours from UTC time
	# this number is subtracted from UTC time, so should be positive if going west
	timeOffset = db.IntegerProperty(default = 8)