#!/usr/bin/env python

import os
import cloudstorage as gcs
import webapp2
import re
import logging

my_default_retry_params = gcs.RetryParams(initial_delay=0.2,
                                          max_delay=5.0,
                                          backoff_factor=2,
                                          max_retry_period=15)
gcs.set_default_retry_params(my_default_retry_params)

class ConfigBasePage(webapp2.RequestHandler):

    def sendConfig(self, domain):
        try:
            gcs_file = gcs.open('/clickcounter/domain/' + self.request.get('domain'))
            self.response.write(gcs_file.read())
            gcs_file.close()
        except:
            try:
                logging.info('no configuration found for ' + self.request.get('domain'));
                gcs_file = gcs.open('/clickcounter/domain/default')
                self.response.write(gcs_file.read())
                gcs_file.close()            
            except:
                logging.error('no default configuration found');
                self.error(500);
                self.response.write('{}\n');    

class MainPage(ConfigBasePage):

    def post(self):
        if not re.search(r"^[^/]+$", self.request.get('domain')):
            self.error(403);
            self.response.write('Expected domain name to match ^[^/]+$, but got \'' + self.request.get('domain') + '\'\n')
            logging.info('refused to service configuration for \'' + self.request.get('domain') + '\'');
            return
        self.response.headers['Content-Type'] = 'application/json'
        if 'Origin' in self.request.headers:
            self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']    
        self.sendConfig(self.request.get('domain'))    

class ConfigPage(ConfigBasePage):

    # TODO require login
    def get(self, domain):
        self.sendConfig(domain)

    # TODO require login
    def post(self, domain):
        write_retry_params = gcs.RetryParams(backoff_factor=1.1)
        gcs_file = gcs.open('/clickcounter/domain/' + domain,
                            'w',
                            content_type='application/json',
                            options={},
                            retry_params=write_retry_params)
        gcs_file.write(self.request.body)
        gcs_file.close()
        
    # TODO require login
    def delete(self, domain):
        try:
            gcs.delete('/clickcounter/domain/' + domain)
        except gcs.NotFoundError:
            pass

class JSPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/javascript'
        if 'Origin' in self.request.headers:
            self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']
        try:
            gcs_file = gcs.open('/clickcounter/banner.min.js')
            self.response.write(gcs_file.read())
            gcs_file.close()
        except:
            logging.error('could not find banner.min.js');
            self.error(500);
            self.response.write('');


class HTMLCenterPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        if 'Origin' in self.request.headers:
            self.response.headers['Access-Control-Allow-Origin'] = self.request.headers['Origin']
        try:
            gcs_file = gcs.open('/clickcounter/banner-center.html')
            self.response.write(gcs_file.read())
            gcs_file.close()
        except:
            logging.error('could not find banner-center.html');
            self.error(500);
            self.response.write('');        

application = webapp2.WSGIApplication([
    ('/c', MainPage),
    (r'/config/(.*)', ConfigPage),
    ('/banner.min.js', JSPage),
    ('/banner-center.html', HTMLCenterPage),
], debug=True)

