import cgi
import os
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from controllers.pairController import *
from models.categoryModel import *
from models.userPreferencesModel import *
from controllers.categoryController import *
from controllers.userPreferencesController import *

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		categoryQuery = Category.all().filter('owner =', user)
		categoryQuery.order('name')
		categories = categoryQuery.fetch(100)
		
		# create a preferences object if they don't have one (is there a better place?)
		prefs = UserPreferences.all().filter('user =', user).fetch(1)
		if len(prefs) == 0:
			newPrefs = UserPreferences(user = user)
			newPrefs.put()
		
		logout = users.create_logout_url(self.request.uri)
		
		template_values = {
			'logout': logout,
			'categories': categories,
			}
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))

		

application = webapp.WSGIApplication(
									[('/', MainPage), 
									('/new-category', NewCategoryForm),
									('/add-category', AddCategoryAction),
									('/edit-category', EditCategoryForm),
									('/change-category', EditCategoryAction),
									('/delete-category', DeleteCategory),
									('/new-pair', NewPairForm),
									('/add-pair', AddPairAction),
									('/edit-pair', EditPairForm),
									('/change-pair', EditPairAction),
									('/delete-pair', DeletePair),
									('/view-pairs', ViewPairs),
									('/view-stats', ViewStats),
									('/start-review', StartReviewAction),
									('/category', CategoryPage),
									('/update-pair', UpdatePairAction),
									('/edit-settings', EditSettingsForm),
									('/change-settings', EditSettingsAction),
									],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
