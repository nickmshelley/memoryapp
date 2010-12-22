from models.userPreferencesModel import UserPreferences
import unittest
import datetime
import os
from datetime import timedelta
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError
from google.appengine.api import user_service_stub 
from webtest import TestApp
from cards import application


class TestUserPreferencesController(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		AUTH_DOMAIN = 'gmail.com' 
		LOGGED_IN_USER = 'test@example.com'
		apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
		os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
		os.environ['USER_EMAIL'] = LOGGED_IN_USER
		
		self.user = user = User(email = "test@example.com")
	
		self.app = TestApp(application)
	
	def testEditSettingsForm(self):
		# set up the default preferences
		prefs = UserPreferences(user = self.user)
		prefs.put()
		
		# make sure offset is prepopulated
		offset = prefs.timeOffset
		response = str(self.app.get('/edit-settings'))
		self.assertTrue(str(offset) in response)
		
		prefs.timeOffset = 100
		prefs.put()
		
		response = str(self.app.get('/edit-settings'))
		self.assertTrue("100" in response)
	
	def testEditSettingsAction(self):
		# set up preferences
		prefs = UserPreferences(user = self.user, timeOffset = 2)
		prefs.put()
		
		# make sure offset changes
		self.app.post('/change-settings', {'offset': '5'})
		prefs = UserPreferences.all().filter('user =', self.user).fetch(1)[0]
		offset = prefs.timeOffset
		self.assertEquals(offset, 5)
