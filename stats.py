# app stats handlers
import webapp2

from google.appengine.api import memcache


class ClickCount(webapp2.RequestHandler):
    """
    returns the total clickcount
    """

    def get(self):
        clickcount = memcache.get("clicks_total")
        if clickcount is None:
            # memcache will be filled some time in the future
            self.abort(503)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write(clickcount)
