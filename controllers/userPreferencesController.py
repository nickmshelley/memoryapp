from models.userPreferencesModel import UserPreferences
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.api import users
import os
import datetime
import random

class EditSettingsForm(webapp.RequestHandler):
	def get(self):
		logout = users.create_logout_url(self.request.uri)
		prefs = UserPreferences.getUserPreferences()
		offset = prefs.timeOffset
		path = os.path.join(os.path.dirname(__file__), '../templates/edit_settings.html')
		utcTime = datetime.datetime.now()
		utcTime = utcTime.strftime("%D %r")
		myTime = datetime.datetime.now() - datetime.timedelta(hours=offset) # adjust for utc time
		myTime = myTime.strftime("%D %r")
		self.response.out.write(template.render(path, {'preferences': prefs,
														'utcTime': utcTime,
														'myTime': myTime,
														'logout': logout
														}))

class EditSettingsAction(webapp.RequestHandler):
	def post(self):
		prefs = UserPreferences.getUserPreferences()
		offset = self.request.get('offset')
		try:
			prefs.timeOffset = int(offset)
			prefs.updateDbAndCache()
		except ValueError:
			pass
		self.redirect('/edit-settings')