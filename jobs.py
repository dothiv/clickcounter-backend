#!/usr/bin/env python

import webapp2
from models import Domain
from google.appengine.api import memcache
import handlers
import logging
import models
from google.appengine.ext import deferred


def update_total_clicks():
    """
    Updates the memcached total clickcount value
    """
    clicks = 0
    for domain in Domain.query():
        clicks = clicks + domain.clickcount
    memcache.set('clicks_total', clicks)


def update_clicks(domainname):
    """
    Updates the memcached total clickcount value
    """
    domain = Domain.query(Domain.name == str(domainname)).get()
    if domain:
        memcache.set(get_cache_key(domain), domain.clickcount)


def init_clicks_total():
    """
    Initialize the memcached total click counter
    """
    memcache.set('clicks_total', 1)
    deferred.defer(update_total_clicks)


def init_clicks(domain):
    """
    Initialize the memcached click counter for the given domain
    """
    memcache.set(get_cache_key(domain), domain.clickcount + 1)
    deferred.defer(update_clicks, domain.name)


def get_cache_key(domain):
    return 'domain:c:' + domain.name


class CounterPersist(webapp2.RequestHandler):
    """
    Task handler which persist the memcache counters.
    It's call by the app engine cron.
    """
    def get(self):
        if self.request.headers.get('X-AppEngine-Cron') != "true":
            self.error(403)
            return
        for domain in Domain.query():
            # TODO: Maybe maintain a list of domains which do have a memcache counter?
            new_count = memcache.get(get_cache_key(domain))
            if new_count < domain.clickcount:
                logging.error("New clickcount for %s would be %d, is %d", domain.name, new_count, domain.clickcount)
            elif not new_count:
                logging.info("No clickcount in memcache for: %s", domain.name)
            elif new_count == domain.clickcount:
                logging.info("clickcount for %s unchanged: %d", domain.name, new_count)
            else:
                domain.clickcount = new_count
                domain.put()
                logging.info("clickcount for %s: %d -> %d", domain.name, domain.clickcount, new_count)


class TotalPersist(webapp2.RequestHandler):
    """
    Task handler which persist the total click counts at the current time
    It's call by the app engine cron.
    """
    def get(self):
        if self.request.headers.get('X-AppEngine-Cron') != "true":
            self.error(403)
            return
        total = 0
        for domain in Domain.query():
            mem_count = memcache.get(get_cache_key(domain))
            if mem_count:
                total = total + mem_count
            else:
                total = total + domain.clickcount
        ct = models.ClickcountDate()
        ct.clickcount = total
        ct.put()