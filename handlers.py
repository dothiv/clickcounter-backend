# app handlers
import webapp2

from settings import JINJA_ENVIRONMENT
from models import Domain, StaticFile, UserData
from decorators import basic_auth


def get_domain_or_404(name, allow_none=False):
  """Gets a domain entity for the given name.

  Aborts with 404 if entity doesn't exist and if that is not allowed.
  """
  if not name:
    webapp2.abort(404)

  domain = Domain.query(Domain.name==name).get()
  if not domain and not allow_none:
    webapp2.abort(404)

  return domain



class Index(webapp2.RequestHandler):
    """
    Handler Index

    Implements GET only and renders a simple page template
    """

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('page.html')
        self.response.write(template.render())


class Config(webapp2.RequestHandler):
  """
  Handler Config

  GET: show a domain's configuration as JSON (text/plain)
  POST: edit or create a domain's configuration, responds with 204
  DELETE: delete a domain's configuration, responds with 204

  All HTTP methods are protected by HTTP Basic Auth.
  """

  @basic_auth
  def get(self, domain_name):
    domain = get_domain_or_404(domain_name)
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write(domain.get_json())


  @basic_auth
  def post(self, domain_name):
    domain = get_domain_or_404(domain_name, allow_none=True)
    if not domain:
      domain = Domain(name=domain_name, clickcount=0, money=0., status=0.)
    # example content:
    # "firstvisit":"center","secondvisit":"center","heading":"Vielen Dank!","subheading":"Dein Klick auf domain.hiv hat soeben einen Gegenwert von 1&thinsp;ct ausgel&ouml;st.","claim":"Wir sind Teil der Bewegung","about":"&Uuml;ber dotHIV","vote":"Vote","activated":"Bisher aktiviert:","currency":"&euro;","corresponding":"entspricht","clicks":"Klicks"
    domain.content = self.request.body
    domain.put()

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


  @basic_auth
  def delete(self, domain_name):
    domain = Domain.query(Domain.name==domain_name).get()
    if domain:
      domain.key.delete()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


class Count(webapp2.RequestHandler):
  """
  Handler Count

  POST: increment click count if certain parameters are valid
  """

  def post(self):
    params = self.request.params
    if not 'domain' in params:
      self.abort(404)

    domain = get_domain_or_404(params['domain'])
    if 'from' in params and 'firstvisit' in params:
      if params['from'] == 'inside' and params['firstvisit'] == 'true':
        domain.increment_counter()
        UserData.add(self.request, params['domain'])

    # explicit request to have content-type application/json
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(domain.get_json())


class StaticServe(webapp2.RequestHandler):

  @basic_auth
  def post(self, file_name):
    static_file = StaticFile.query(StaticFile.name==file_name).get()
    if not static_file:
      static_file = StaticFile(name=file_name)

    static_file.content = self.request.body
    static_file.content_type = self.get_content_type(self.request.headers)
    static_file.put()

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)

  def get(self, file_name):
    static_file = StaticFile.query(StaticFile.name==file_name).get()
    if not static_file:
      self.abort(404)
    else:
      self.response.write(static_file.content)
      self.response.set_status(200)
      self.response.headers['Content-Type'] = str(static_file.content_type)
      self.response.headers['Access-Control-Allow-Origin'] = '*'

  def get_content_type(self, headers):
    if 'Content-Type' in headers:
      content_type = headers['Content-Type']
    else:
      file_extension = file_name.split('.')[-1]
      if file_extension == 'js':
        content_type = 'application/javascript'
      elif file_extension == 'html':
        content_type = 'text/html'
      else:
        content_type = 'text/plain'
    return content_type