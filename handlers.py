# app handlers
import webapp2

from settings import JINJA_ENVIRONMENT, ALREADY_DONATED, ALREADY_CLICKED, EUR_GOAL, EUR_INCREMENT
from models import Domain, StaticFile, UserData
from decorators import basic_auth
from webapp2_extras import json
from util import Format
from google.appengine.api import memcache

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


def createDomainConfig(domain):
    """
    TODO: Cache?
    """
    config = json.decode('{%s}' % domain.content) if domain.content else {}

    # Fetch global values
    m = memcache.get_multi(['clicks_total', 'already_donated', 'already_clicked', 'eur_goal'])
    if 'already_clicked' not in m:
        memcache.set('already_clicked', ALREADY_CLICKED)
        already_clicked = ALREADY_CLICKED
    else:
        already_clicked = m['already_clicked']

    if 'already_donated' not in m:
        memcache.set('already_donated', ALREADY_DONATED)
        already_donated = ALREADY_DONATED
    else:
        already_donated = m['already_donated']

    if 'eur_goal' not in m:
        memcache.set('eur_goal', EUR_GOAL)
        goal = EUR_GOAL
    else:
        goal = m['eur_goal']

    clicks_total = m['clicks_total'] if 'clicks_total' in m else 0
    clicks = clicks_total - already_clicked

    ## Plain values
    config['donated'] = float(already_donated)
    unlocked = clicks * EUR_INCREMENT
    config['unlocked'] = unlocked
    config['percent'] = unlocked / goal
    config['clicks'] = clicks
    config['increment'] = EUR_INCREMENT

    # Create labels
    f = Format(config["locale"] if "locale" in config else None)
    labels = {
        'donated': f.decimalMoney(already_donated),
        'unlocked': f.money(unlocked),
        'clicks': f.decimal(clicks),
        'increment': f.float(EUR_INCREMENT * 100.0)
    }
    for key in config:
        if isinstance(config[key], basestring):
            config[key] = config[key].format(**labels)

    return json.encode(config)



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
      # count clicks from outside the iframe that are the first visit
      # we may need to count clicks with from=inside as well, work in progress
      if params['from'] == 'outside' and params['firstvisit'] == 'true':
        # maybe use a transaction for these two independent database
        # operations? maybe not: it doesn't really matter if an entity of
        # UserData could be put while Domain failed or vice versa.
        domain.increment_counter()
        UserData.add(self.request, params['domain'])

    # explicit request to have content-type application/json
    self.response.headers['Content-Type'] = 'application/json'
    # allow origin
    if 'Origin' in self.request.headers:
      self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']
    self.response.write(domain.get_json())


class StaticServe(webapp2.RequestHandler):

  @basic_auth
  def post(self, file_name):
    static_file = StaticFile.query(StaticFile.name==file_name).get()
    if not static_file:
      static_file = StaticFile(name=file_name)

    static_file.content = self.request.body
    static_file.content_type = self.get_content_type(
      self.request.headers, file_name)
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


  def get_content_type(self, headers, file_name):
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
