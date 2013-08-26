#!/usr/bin/env python

import webapp2
import views

application = webapp2.WSGIApplication([
    ('/', views.Index),
    (r'/config/(.*)', views.Config),
], debug=True)
