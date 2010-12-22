from models.userPreferencesModel import UserPreferences
import unittest
import datetime
from datetime import timedelta
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError


class TestUserPreferencesModel(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
	
	def testCreation(self):
		user = User(email = "test@foo.com")
		self.assertRaises(BadValueError, UserPreferences)
		
		prefs = UserPreferences(user = user)
		self.assertEquals(prefs.user, user)
		self.assertEquals(prefs.timeOffset, 8)
		
		prefs = UserPreferences(user = user, timeOffset = 10)
		self.assertEquals(prefs.user, user)
		self.assertEquals(prefs.timeOffset, 10)