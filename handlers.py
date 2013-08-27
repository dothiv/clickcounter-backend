# app handlers
import os, webapp2, jinja2

from settings import JINJA_ENVIRONMENT
from models import Domain
from decorators import basic_auth


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

  def _get_domain_data(self, domain, allow_none=False):
    """Gets a data storage entity for the given domain"""
    if not domain:
      self.abort(404)

    data = Domain.query(Domain.name==domain).fetch(1)
    if len(data) < 1:
      if allow_none:
        return None
      else:
        self.abort(404)

    return data[0]


  @basic_auth
  def get(self, domain):
    data = self._get_domain_data(domain)
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.write(data.get_json())


  @basic_auth
  def post(self, domain):
    data = self._get_domain_data(domain, allow_none=True)
    if not data:
      data = Domain(name=domain, clickcount=0, money=0., status=0.)
    # example content:
    # "firstvisit":"center","secondvisit":"center","heading":"Vielen Dank!","subheading":"Dein Klick auf domain.hiv hat soeben einen Gegenwert von 1&thinsp;ct ausgel&ouml;st.","claim":"Wir sind Teil der Bewegung","about":"&Uuml;ber dotHIV","vote":"Vote","activated":"Bisher aktiviert:","currency":"&euro;","corresponding":"entspricht","clicks":"Klicks"
    data.content = self.request.body
    data.put()

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


  @basic_auth
  def delete(self, domain):
    data = self._get_domain_data(domain)
    data.key.delete()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


class Count(webapp2.RequestHandler):
  """
  Handler Count

  POST: increment click count if certain parameters are valid
  """

  def _get_domain_data(self, domain):
    """Gets a data storage entity for the given domain."""
    data = Domain.query(Domain.name==domain).fetch(1)
    if len(data) < 1:
        self.abort(404)
    return data[0]


  def post(self):
    params = self.request.params
    if not 'domain' in params:
      self.abort(404)

    data = self._get_domain_data(params['domain'])
    if 'from' in params and 'firstvisit' in params:
      if params['from'] == 'inside' and params['firstvisit'] == 'true':
        data.increment()

    # explicit request to have content-type application/json
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(data.get_json())
