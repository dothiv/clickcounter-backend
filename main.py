#!/usr/bin/env python

import webapp2

application = webapp2.WSGIApplication([
    ('/', 'handlers.Index'),
    (r'/config/(.*)', 'handlers.Config'),
    (r'/c/?', 'handlers.Count'),
], debug=True)
