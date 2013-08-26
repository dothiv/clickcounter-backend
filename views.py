# app views

import os, webapp2, jinja2
from settings import JINJA_ENVIRONMENT
from models import Domain
from decorators import basic_auth


class Config(webapp2.RequestHandler):
  def get_domain_data(self, domain, allow_none=False):
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
    data = self.get_domain_data(domain)
    # this is not valid JSON, but required like that by banner.min.js
    self.response.headers['Content-Type'] = 'text/plain'
    json = '{%s "clickcount":"%s", "money":"%s", "status":"%s"}' % (
      data.content, data.clickcount, data.money, data.status
    )
    self.response.write(json)


  @basic_auth
  def post(self, domain):
    data = self.get_domain_data(domain, allow_none=True)
    if not data:
      data = Domain(name=domain, clickcount=0, money=0., status=0.)
    data.content = self.request.body
    data.put()

    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


  @basic_auth
  def delete(self, domain):
    data = self.get_domain_data(domain)
    data.key.delete()
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.set_status(204)


class Index(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('page.html')
        self.response.write(template.render())
