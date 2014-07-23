# app handlers
import webapp2

from settings import JINJA_ENVIRONMENT, ALREADY_DONATED, ALREADY_CLICKED, EUR_GOAL, EUR_INCREMENT, COUNT_THRESHOLD
from models import Domain
from decorators import basic_auth
from webapp2_extras import json
from util import Format
from google.appengine.api import memcache
import jobs
from random import random

"""
Gets a domain entity for the given name.

Aborts with 404 if entity doesn't exist and if that is not allowed.
"""
def get_domain_or_404(name, allow_none=False):
    if not name:
        webapp2.abort(404)

    domain = Domain.query(Domain.name == name).get()
    if not domain and not allow_none:
        webapp2.abort(404)

    return domain


def createDomainConfig(domain, client_locales):
    """
    TODO: Cache?
    """
    config = json.decode(domain.content) if domain.content else {}

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
    locale = 'en'
    if 'default_locale' in config:
        locale = config['default_locale']
        del config['default_locale']

    # Get client locale
    for client_locale in client_locales:
        if client_locale in config['__locales']:
            locale = client_locale
            break
    del config['__locales']
    f = Format(locale)
    labels = {
        'donated': f.decimalMoney(already_donated),
        'unlocked': f.money(unlocked),
        'clicks': f.decimal(clicks),
        'increment': f.money(EUR_INCREMENT)
    }
    if 'strings' in config:
        for key in config['strings'][locale]:
            if isinstance(config['strings'][locale][key], basestring):
                config[key] = config['strings'][locale][key]
                for labelkey in labels:
                    config[key] = config[key].replace('%' + labelkey + '%', labels[labelkey])
        del config['strings']
    return json.encode(config)

"""
Parse the value in a Accept-Language Header

@see http://cvmlrobotics.blogspot.de/2012/10/detect-user-language-locale-on-google.html
"""
def getClientLocales(acceptLanguage):
    if not acceptLanguage:
        return ['en']
    languages = acceptLanguage.split(",")
    locale_q_pairs = []

    for language in languages:
        if language.split(";")[0] == language:
            # no q => q = 1
            locale_q_pairs.append((language.strip(), "1"))
        else:
            locale = language.split(";")[0].strip()
            q = language.split(";")[1].split("=")[1]
            locale_q_pairs.append((locale, q))

    sorted_pairs = sorted(locale_q_pairs, key=lambda lang: lang[1], reverse=True)
    return map(lambda lang: lang[0], sorted_pairs)

class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message


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
        self.response.write(createDomainConfig(domain, getClientLocales(self.request.headers.get('accept-language'))))

    @basic_auth
    def post(self, domain_name):
        domain = get_domain_or_404(domain_name, allow_none=True)
        if not domain:
            domain = Domain(name=domain_name, clickcount=0, money=0.)
        data = self.request.body.strip()
        config = json.decode(data) if len(data) > 0 else {}
        config['__locales'] = []
        if 'strings' in config:
            for locale in config['strings']:
                config['__locales'].append(locale)
        domain.content = json.encode(config)
        domain.put()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.set_status(204)


    @basic_auth
    def delete(self, domain_name):
        domain = Domain.query(Domain.name == domain_name).get()
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

        cache_key_domain = 'domain:d:' + params['domain']

        domain = memcache.get(cache_key_domain)
        if domain == 0:
            self.abort(404)
            return
        if not domain:
            domain = Domain.query(Domain.name == params['domain']).get()
            if not domain:
                # store for 60 seconds
                memcache.set(cache_key_domain, 0, 60)
                self.abort(404)
                return
            else:
                memcache.set(cache_key_domain, domain, 60)

        # count clicks from outside the iframe that have a previous (pt) and current (ct) visit timestamp
        # previous timestamp may be empty if the client has no record of this user having visited the domain before)
        # current timestamp may not be empty
        # for simplicity timestamps are expressed as integers (unix timestamps) in the users timezone
        try:
            if 'from' in params and 'pt' in params and 'ct' in params:
                if params['from'] == 'outside':
                    current_visit = int(params['ct']) if params['ct'] != "" else 0
                    if current_visit < 1397340000000:
                        raise Error("Invalid value for 'ct': '%s'" % params['ct'])

                    previous_visit = int(params['pt']) if params['pt'] != "" else current_visit - COUNT_THRESHOLD
                    if previous_visit < 1397340000000:
                        raise Error("Invalid value for 'pt': '%s'" % params['pt'])

                    if current_visit < previous_visit:
                        raise Error("Value '%s' for 'ct' must be greater or equal than value '%s' for 'pt'" % (params['ct'], params['pt']))

                    if current_visit - previous_visit >= COUNT_THRESHOLD:
                        if memcache.incr(jobs.get_cache_key(domain)) is None:
                            jobs.init_clicks(domain)
                        if memcache.incr("clicks_total") is None:
                            jobs.init_clicks_total()
        except Error as e:
            self.response.headers['Content-Type'] = 'application/api-problem+json'
            self.response.set_status(403)
            self.response.write(
                json.encode(
                    {
                        "problemType": "https://github.com/dothiv/clickcounter-backend/wiki/problem-invalid-request",
                        "title": "%s" % e.message
                    }
                )
            )
            return

        # explicit request to have content-type application/json
        self.response.headers['Content-Type'] = 'application/json'
        # allow origin
        if 'Origin' in self.request.headers:
            self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']
        self.response.write(createDomainConfig(domain, getClientLocales(self.request.headers.get('accept-language'))))
