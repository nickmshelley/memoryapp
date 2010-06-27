import cgi
import os
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from pair import *
from category import *

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		categoryQuery = Category.all().order('name')
		categoryQuery.filter('owner =', user)
		categories = categoryQuery.fetch(10)
		
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
									('/new-pair', NewPairForm),
									('/add-pair', AddPairAction),
									('/category', CategoryPage),
									('/update-pair', UpdatePairAction),
									('/mark-review', MarkReviewAction),
									],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
