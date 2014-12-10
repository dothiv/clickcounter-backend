# redirects handlers
import webapp2
import re
from webapp2_extras import json
from models import Domain
from urlparse import urlparse
import csv

class List(webapp2.RequestHandler):
    """
    List configured redirects

    TODO: Implement ETag / Last-Modified handling
    """

    def get(self):
        if 'Accept' in self.request.headers:
            if self.request.headers['Accept'] == 'application/json':
                self.list_redirects_json()
                return
            if self.request.headers['Accept'] == 'text/csv':
                self.list_redirects_csv()
                return
        webapp2.abort(406)


    def list_redirects_json(self):

        redirects = []

        domains = Domain.query(Domain.redirect_enabled == True)
        for domain in domains.iter():
            host = urlparse(domain.redirect_url)
            rule = dict(hosts=[host.netloc])
            rule["rules"] = [
                {"from": "^" + re.escape(domain.redirect_url), "to": "http://" + domain.name + "/"}]

            if re.match('^www\.', host.netloc):
                # Add rule without www
                rule["hosts"].append(host.netloc[4:])
                nowww_redirect_url = re.sub('//www\.', '//', domain.redirect_url)
                rule["rules"].append({"from": "^" + re.escape(nowww_redirect_url), "to": "http://" + domain.name + "/"})
            else:
                # Add rule with www
                rule["hosts"].append("www." + host.netloc)
                www_redirect_url = re.sub('(https*://)', '\g<1>www.', domain.redirect_url)
                rule["rules"].append({"from": "^" + re.escape(www_redirect_url), "to": "http://" + domain.name + "/"})

            rule["exceptions"] = []
            redirects.append(rule)

        self.response.headers['Content-Type'] = 'application/json'
        self.response.write(json.encode(redirects))


    def list_redirects_csv(self):

        self.response.headers['Content-Type'] = 'text/csv'

        writer = csv.writer(self.response, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        domains = Domain.query(Domain.redirect_enabled == True)
        for domain in domains.iter():
            writer.writerow([domain.name, domain.redirect_url])
