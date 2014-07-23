#!/usr/bin/env python

import webapp2
from models import Domain
from google.appengine.api import memcache
import handlers
import logging
from google.appengine.ext import deferred

"""
Updates the memcached total clickcount value
"""
def update_total_clicks():
    clicks = 0
    for domain in Domain.query():
        clicks = clicks + domain.clickcount
    memcache.set('clicks_total', clicks)


"""
Updates the memcached total clickcount value
"""
def update_clicks(domainname):
    domain = Domain.query(Domain.name == str(domainname)).get()
    if domain:
        memcache.set(get_cache_key(domain), domain.clickcount)

"""
Initialize the memcached total click counter
"""
def init_clicks_total():
    memcache.set('clicks_total', 1)
    deferred.defer(update_total_clicks)

"""
Initialize the memcached click counter for the given domain
"""
def init_clicks(domain):
    memcache.set(get_cache_key(domain), domain.clickcount + 1)
    deferred.defer(update_clicks, domain.name)

def get_cache_key(domain):
    return 'domain:c:' + domain.name

"""
Task handler which persist the counters.
It's call by the app engine cron.
"""
class CounterPersist(webapp2.RequestHandler):
    """
    Persist memcache counters
    """
    def get(self):
        if self.request.headers.get('X-AppEngine-Cron') != "true":
            self.error(403)
            return
        for domain in Domain.query():
            new_count = memcache.get(get_cache_key(domain))
            if new_count < domain.clickcount:
                logging.error("New clickcount for %s would be %d, is %d", domain.name, new_count, domain.clickcount)
            else:
                domain.clickcount = new_count
                domain.put()
                logging.info("clickcount for %s: %d -> %d", domain.name, domain.clickcount, new_count)
