#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, base64, unittest, time

# get app engine's resources
SDK_PATH = sys.argv.pop() if len(sys.argv) > 1 else './google_appengine'

print 'Using SDK path %s' % SDK_PATH

sys.path.insert(0, SDK_PATH)
import dev_appserver

dev_appserver.fix_sys_path()
from webapp2 import Request
from webapp2_extras import json
from google.appengine.ext import testbed

from main import application
from settings import get_auth_secret, set_auth_secret, COUNT_THRESHOLD, EUR_INCREMENT
from google.appengine.api import memcache
import pickle
import jobs
import models
from datetime import datetime


class TestCase(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_taskqueue_stub()
        cfg = set_auth_secret("somesecret")
        self.auth_header = (
            'Authorization', 'Basic %s' % base64.b64encode(':' + cfg.value)
        )
        self.domain = 'foobar'
        self.uri_config = '/config/' + self.domain

    def tearDown(self):
        # Run pending jobs
        taskq = self.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)
        tasks = taskq.GetTasks("default")
        taskq.FlushQueue("default")
        while tasks:
            for task in tasks:
                (func, args, opts) = pickle.loads(base64.b64decode(task["body"]))
                func(*args)
            tasks = taskq.GetTasks("default")
            taskq.FlushQueue("default")

        self.testbed.deactivate()


    def _create_config(self, body=None):
        """Helper to create a basic domain config.

        Returns the response object.
        """
        request = Request.blank(self.uri_config, headers=[self.auth_header])
        request.method = 'POST'
        request.body = body
        return request.get_response(application)


    def test_config_post(self):
        memcache.set('already_donated', 0)
        memcache.set('already_clicked', 0)
        memcache.set('eur_goal', 1)

        body = '{"foo":"bar"}'
        response = self._create_config(body=body)
        self.assertEqual(response.status_int, 204)
        self.assertEqual(response.body, '')

        body = '{"foo":"bar", "clicks":0, "clicks_domain":0, "donated":0.0, "unlocked": 0.0, "percent":0.0, "increment": %f}' % EUR_INCREMENT
        request = Request.blank(self.uri_config, headers=[self.auth_header])
        response = request.get_response(application)
        self._compareJson(response.body, body)


    def test_config_get_fail(self):
        # nothing at root
        response = application.get_response('/config')
        self.assertEqual(response.status_int, 404)

        # basic auth fail
        response = application.get_response(self.uri_config)
        self.assertEqual(response.status_int, 401)

        # basic auth success, but domain doesn't exist yet
        request = Request.blank(self.uri_config, headers=[self.auth_header])
        response = request.get_response(application)
        self.assertEqual(response.status_int, 404)


    def test_config_get_success(self):
        self._create_config()
        request = Request.blank(self.uri_config, headers=[self.auth_header])
        response = request.get_response(application)
        self.assertEqual(response.status_int, 200)


    def test_config_delete(self):
        self._create_config()

        # get 204 on actual delete
        request = Request.blank(self.uri_config, headers=[self.auth_header])
        request.method = 'DELETE'
        response = request.get_response(application)
        self.assertEqual(response.status_int, 204)

        # still get 204 on delete after deletion
        response = request.get_response(application)
        self.assertEqual(response.status_int, 204)


    def test_c_get(self):
        # no GET for /c
        response = application.get_response('/c')
        self.assertEqual(response.status_int, 405)


    def test_c_post_noexist(self):
        self._create_config()

        uri = '/c?domain=dontexist'
        request = Request.blank(uri, headers=[self.auth_header])
        request.method = 'POST'
        response = request.get_response(application)
        self.assertEqual(response.status_int, 404)


    def _test_c_post(self, uri, body, status=200):
        """Helper to actually test posting to /c, depending on uri and body."""
        request = Request.blank(uri, headers=[self.auth_header])
        request.method = 'POST'
        response = request.get_response(application)
        self.assertEqual(response.status_int, status)
        self._compareJson(response.body, body)

    def _sortDict(self, d):
        r = {}
        for k in sorted(d.iterkeys()):
            r[k] = d[k]
        return r


    def _compareJson(self, actual, expected):
        self.assertEqual(json.encode(self._sortDict(json.decode(actual))),
                         json.encode(self._sortDict(json.decode(expected))))

    def test_c_post_count(self):
        self._create_config()

        memcache.set('already_donated', 0)
        memcache.set('already_clicked', 0)
        memcache.set('eur_goal', 1)

        # all values should still be 0 after request from inside
        uri = '/c?domain=' + self.domain + '&from=inside'
        body = '{"clicks":0, "donated":0.0, "unlocked": 0.0, "percent":0.0, "increment": %f}' % EUR_INCREMENT
        self._test_c_post(uri, body)

        # from == outside, no previous visit, with current timestamp increases counter
        now = int(time.time() * 1000)
        current_time = "%d" % now
        uri = '/c?domain=' + self.domain + '&from=outside&pt=&ct=' + current_time
        body = '{"clicks":1, "donated":0.0, "unlocked": %f, "percent":%f, "increment": %f}' % (EUR_INCREMENT, EUR_INCREMENT, EUR_INCREMENT)
        self._test_c_post(uri, body)

        # from == outside, previous visit 1 second before current timestamp does not increase counter
        uri = '/c?domain=' + self.domain + '&from=outside&pt=' + ("%s" % (now - 1)) + '&ct=' + current_time
        self._test_c_post(uri, body)

        # from == outside, previous visit before current timestamp increases counter
        uri = '/c?domain=' + self.domain + '&from=outside&pt=' + (
            "%s" % (now - COUNT_THRESHOLD)) + '&ct=' + current_time
        body = '{"clicks":2, "donated":0.0, "unlocked": %f, "percent":%f, "increment": %f}' % (2 * EUR_INCREMENT, 2 * EUR_INCREMENT, EUR_INCREMENT)
        self._test_c_post(uri, body)

        self.assertEquals(2, memcache.get('clicks_total'))
        d = models.Domain()
        d.name = self.domain
        self.assertEquals(2, memcache.get(jobs.get_cache_key(d)))

        # Pre-cron
        domain = models.Domain.query(models.Domain.name == str(self.domain)).get()
        self.assertEquals(0, domain.clickcount)
        count = models.ClickcountDate.query().get()
        self.assertTrue(count is None)

        # Execute memcount cron
        request = Request.blank('/task/counter/persist', headers=[('X-AppEngine-Cron', 'true')])
        request.method = 'GET'
        request.get_response(application)
        domain = models.Domain.query(models.Domain.name == str(self.domain)).get()
        self.assertEquals(2, domain.clickcount)

        # Execute total cron
        request = Request.blank('/task/total/persist', headers=[('X-AppEngine-Cron', 'true')])
        request.method = 'GET'
        request.get_response(application)
        count = models.ClickcountDate.query().get()
        self.assertEquals(2, count.clickcount)
        self.assertEquals(datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"), count.time.strftime("%Y-%m-%dT%H:%M:%S"))

    def test_c_post_error(self):
        self._create_config()
        now = time.time() * 1000
        current_time = "%d" % now
        body_template = '{"problemType":"https://github.com/dothiv/clickcounter-backend/wiki/problem-invalid-request","title":"%s"}'
        # Error on invalid ct
        body = body_template % "Invalid value for 'ct': ''"
        self._test_c_post('/c?domain=' + self.domain + '&from=outside&pt=&ct=', body, status=403)
        body = body_template % "Invalid value for 'ct': '1234'"
        self._test_c_post('/c?domain=' + self.domain + '&from=outside&pt=&ct=1234', body, status=403)
        # Error on invalid pt
        body = body_template % "Invalid value for 'pt': '1234'"
        self._test_c_post('/c?domain=' + self.domain + '&from=outside&pt=1234&ct=' + current_time, body, status=403)
        pt_to_high = "%d" % (now + 1)
        body = body_template % (
            "Value '" + current_time + "' for 'ct' must be greater or equal than value '" + pt_to_high + "' for 'pt'")
        self._test_c_post('/c?domain=' + self.domain + '&from=outside&pt=' + pt_to_high + '&ct=' + current_time, body,
                          status=403)

    def test_config_replacement(self):
        d = 25000
        memcache.set('already_clicked', d * 1000)
        memcache.set('clicks_total', d * 1000 + 333333)
        memcache.set('already_donated', d)
        memcache.set('eur_goal', 50000)
        memcache.set('eur_increment', EUR_INCREMENT)
        self._create_config(
            '{"firstvisit":"center","secondvisit":"top","default_locale":"en","strings":{'
            + '"en":{"heading":"Thanks!","subheading":"Every click is worth %increment%","about":"More about the <strong>dotHIV</strong> initiative","activated":"Already %donated% contributed:","money":"%unlocked%","clickcount":"%clicks% clicks"},'
            + '"de":{"heading":"Danke!","subheading":"Jeder Klick hilft mit %increment%","about":"Mehr über die <strong>dotHIV</strong> Initiative","activated":"Bereits %donated% gespendet:","money":"%unlocked%","clickcount":"%clicks% Klicks"}}}'
        )
        uri = '/c?domain=' + self.domain + '&from=inside'
        request = Request.blank(uri, headers=[('Accept-Language', 'de,en-US;q=0.5,en;q=0.6')])
        request.method = 'POST'
        response = request.get_response(application)
        config = json.decode(response.body)
        self.assertEqual("Bereits 25.000 &euro; gespendet:", str(config['activated']))
        if EUR_INCREMENT < 0.01: # 0.001
            self.assertEqual("25.333,33 &euro;", str(config['money']))
            self.assertEqual("Jeder Klick hilft mit 0,1 ct", str(config['subheading']))
            self.assertEqual(round(25333.33 / 50000, 3), round(config['percent'], 3))
        else: # 0.01
            self.assertEqual("28.333,33 &euro;", str(config['money']))
            self.assertEqual("Jeder Klick hilft mit 1 ct", str(config['subheading']))
            self.assertEqual(round(28333.33 / 50000, 3), round(config['percent'], 3))
        self.assertEqual("25.333.333 Klicks", str(config['clickcount']))

    # Redirects
    def test_redirects(self):
        self._create_config(
            '{"firstvisit":"center","secondvisit":"top","default_locale":"en","redirect_url":"http://www.example.com/"}'
        )
        headers = [
            ('Accept', 'application/json')
        ]
        request = Request.blank('/redirects', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(200, response.status_int)
        self.assertEqual("application/json", response.headers['Content-Type'])
        redirects = json.decode(response.body)
        self.assertEquals(1, len(redirects))
        self.assertEquals(2, len(redirects[0]['hosts']))
        self.assertEquals(redirects[0]['hosts'][0], 'www.example.com')
        self.assertEquals(redirects[0]['hosts'][1], 'example.com')
        self.assertEquals(redirects[0]['exceptions'], [])
        self.assertEquals(2, len(redirects[0]['rules']))
        self.assertEquals(redirects[0]['rules'][0]['from'], "^http\\:\\/\\/www\\.example\\.com\\/")
        self.assertEquals(redirects[0]['rules'][0]['to'], "http://foobar/")
        self.assertEquals(redirects[0]['rules'][1]['from'], "^http\\:\\/\\/example\\.com\\/")
        self.assertEquals(redirects[0]['rules'][1]['to'], "http://foobar/")

    def test_redirects_nowww(self):
        self._create_config(
            '{"firstvisit":"center","secondvisit":"top","default_locale":"en","redirect_url":"http://example.com/"}'
        )
        headers = [
            ('Accept', 'application/json')
        ]
        request = Request.blank('/redirects', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(200, response.status_int)
        self.assertEqual("application/json", response.headers['Content-Type'])
        redirects = json.decode(response.body)
        self.assertEquals(1, len(redirects))
        self.assertEquals(2, len(redirects[0]['hosts']))
        self.assertEquals(redirects[0]['hosts'][0], 'example.com')
        self.assertEquals(redirects[0]['hosts'][1], 'www.example.com')
        self.assertEquals(redirects[0]['exceptions'], [])
        self.assertEquals(2, len(redirects[0]['rules']))
        self.assertEquals(redirects[0]['rules'][0]['from'], "^http\\:\\/\\/example\\.com\\/")
        self.assertEquals(redirects[0]['rules'][0]['to'], "http://foobar/")
        self.assertEquals(redirects[0]['rules'][1]['from'], "^http\\:\\/\\/www\\.example\\.com\\/")
        self.assertEquals(redirects[0]['rules'][1]['to'], "http://foobar/")


    def test_redirects_csv(self):
        self._create_config(
            '{"firstvisit":"center","secondvisit":"top","default_locale":"en","redirect_url":"http://example.com/"}'
        )
        headers = [
            ('Accept', 'text/csv')
        ]
        request = Request.blank('/redirects', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(200, response.status_int)
        self.assertEqual("text/csv", response.headers['Content-Type'])
        self.assertEqual("foobar,http://example.com/\r\n", response.body)


    def test_redirects_not_acceptable(self):
        headers = [
            ('Accept', 'text/plain')
        ]
        request = Request.blank('/redirects', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(406, response.status_int)

    # Total clickcount

    def test_stats_clickcount(self):
        """
        Test that the API returns the total clickcount
        """
        headers = [
            ('Accept', 'text/plain')
        ]
        # memcache empty
        request = Request.blank('/stats/clickcount', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(503, response.status_int)

        # Fill memcache
        memcache.set('clicks_total', 1234)
        request = Request.blank('/stats/clickcount', headers=headers)
        request.method = 'GET'
        response = request.get_response(application)
        self.assertEqual(200, response.status_int)
        response = request.get_response(application)
        clickcount = int(response.body)
        self.assertEqual(1234, clickcount)

    def test_individual_clickcount(self):
        """
        The config get request should contain the domains individual clickcount
        """
        self._create_config()
        d = models.Domain.query(models.Domain.name == self.domain).get()
        d.clickcount = 1234
        d.put()
        headers = [
            self.auth_header,
            ('Accept', 'text/plain')
        ]
        request = Request.blank(self.uri_config, headers=headers)
        response = request.get_response(application)
        self.assertEqual(response.status_int, 200)
        config = json.decode(response.body)
        self.assertEqual(1234, config['clicks_domain'])


if __name__ == '__main__':
    unittest.main()
