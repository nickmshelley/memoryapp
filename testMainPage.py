from categoryModel import Category
import unittest
import os
from google.appengine.api.users import User
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import datastore_file_stub
from google.appengine.ext.db import BadValueError
from google.appengine.api import user_service_stub 
from webtest import TestApp
from cards import application

class TestMainPage(unittest.TestCase):
	def setUp(self):
		apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
		stub = datastore_file_stub.DatastoreFileStub('memoryapp', '/dev/null', '/dev/null')
		apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
		
		AUTH_DOMAIN = 'gmail.com' 
		LOGGED_IN_USER = 'test@example.com'
		apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
		os.environ['AUTH_DOMAIN'] = AUTH_DOMAIN
		os.environ['USER_EMAIL'] = LOGGED_IN_USER
		
		self.app = TestApp(application)
		
		user1 = User(email = "test@example.com")
		category = Category(owner = user1)
		category.name = 'Hello'
		category.put()
		
		user2 = User(email = "test2@example.com")
		category = Category(owner = user2)
		category.name = 'Goodbye'
		category.put()
	
	def testMainPage(self):
		os.environ['USER_EMAIL'] = "test@example.com"
		response = self.app.get('/')
		self.assertTrue("Hello" in str(response))
		self.assertTrue("Goodbye" not in str(response))
		
		os.environ['USER_EMAIL'] = "test2@example.com"
		response = self.app.get('/')
		self.assertTrue("Goodbye" in str(response))
		self.assertTrue("Hello" not in str(response))
