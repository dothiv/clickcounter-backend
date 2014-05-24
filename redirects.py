# redirects handlers
import webapp2
import os

class List(webapp2.RequestHandler):
    """
    List configured redirects

    TODO: Implement dynamic generation of rules.
    TODO: Implement ETag / Last-Modified handling
    """
    def get(self):
        if 'Accept' in self.request.headers and self.request.headers['Accept'] != 'application/json':
            webapp2.abort(406)
        self.response.headers['Content-Type'] = 'application/json'
        path = os.path.join(os.path.split(__file__)[0], 'example', 'redirects.json')
        with open (path, "r") as f:
            self.response.out.write(f.read())
