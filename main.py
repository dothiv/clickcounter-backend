#!/usr/bin/env python

import webapp2

application = webapp2.WSGIApplication([
    ('/redirects', 'redirects.List'),
    (r'/config/(.*)', 'handlers.Config'),
    (r'/c/?', 'handlers.Count'),
    ('/stats/clickcount', 'stats.ClickCount'),
    ('/task/counter/persist', 'jobs.CounterPersist'),
    ('/task/total/persist', 'jobs.TotalPersist')
])
