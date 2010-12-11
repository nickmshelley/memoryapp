import cgi
import os
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from controllers.pairController import *
from models.categoryModel import *
from controllers.categoryController import *

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		categoryQuery = Category.all().filter('owner =', user)
		categoryQuery.order('name')
		categories = categoryQuery.fetch(100)
		
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
									#('/delete-category', DeleteCategoryAction),
									('/new-pair', NewPairForm),
									('/add-pair', AddPairAction),
									('/edit-pair', EditPairForm),
									('/change-pair', EditPairAction),
									('/delete-pair', DeletePair),
									('/category', CategoryPage),
									('/update-pair', UpdatePairAction),
									('/mark-review', MarkReviewAction),
									('/set-reviewing', SetReviewingAction),
									],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
