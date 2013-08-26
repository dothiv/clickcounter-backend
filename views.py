# app views

from .settings import SECRET
from .models import Domain


def authenticated(request):
  output = False
  authorization = request.headers.get('Authorization')
  if authorization:
    secret = authorization.split("Basic ")[1]
    if secret == SECRET:
      output = True
  return output


def authenticationRequiredResponse(self):
  self.response.headers['Content-Type'] = 'text/plain'
  self.response.set_status(401)
  self.response.write('Unauthorized')


class Config(webapp2.RequestHandler):
  def post(self, domain):
    if authenticated(self.request):
      #TODO: check if the domain exist already then update it
      #save the domain
      self.response.headers['Content-Type'] = 'text/plain'
      self.response.write('config post authenticated')
    else:
      authenticationRequiredResponse(self)


class Index(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Welcome')



