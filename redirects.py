# redirects handlers
import webapp2
import re
from webapp2_extras import json
from models import Domain


class List(webapp2.RequestHandler):
    """
    List configured redirects

    TODO: Implement ETag / Last-Modified handling
    """

    def get(self):
        if 'Accept' in self.request.headers and self.request.headers['Accept'] != 'application/json':
            webapp2.abort(406)

        redirects = []

        domains = Domain.query(Domain.redirect_enabled == True)
        for domain in domains.iter():
            rule = dict(hosts=[domain.name, "*." + domain.name])
            rule["rules"] = [
                {"from": "^" + re.escape(domain.redirect_url), "to": "http://" + domain.name + "/"}]
            rule["exceptions"] = []
            redirects.append(rule)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode(redirects))
