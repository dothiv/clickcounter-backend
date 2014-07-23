#!/usr/bin/env python

import webapp2

application = webapp2.WSGIApplication([
    ('/', 'handlers.Index'),
    ('/redirects', 'redirects.List'),
    (r'/config/(.*)', 'handlers.Config'),
    (r'/c/?', 'handlers.Count'),
    ('/task/counter/persist', 'jobs.CounterPersist')
], debug=True)
