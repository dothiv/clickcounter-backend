import unittest, os, sys, base64

# get app engine's resources
sys.path.insert(0, '../google_appengine')
import dev_appserver
dev_appserver.fix_sys_path()
from webapp2 import Request
from google.appengine.ext import testbed

from main import application
from settings import AUTH_SECRET


class TestCase(unittest.TestCase):
  def setUp(self):
    self.testbed = testbed.Testbed()
    self.testbed.activate()
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.auth_header= (
      'Authorization', 'Basic %s' % base64.b64encode(':' + AUTH_SECRET)
    )
    self.domain = 'foobar'
    self.uri_config = '/config/' + self.domain


  def tearDown(self):
    self.testbed.deactivate()


  def test_index(self):
    response = application.get_response('/')
    self.assertEqual(response.status_int, 200)
    self.assertEqual('banner.min.js' in response.text, True)


  def _create_config(self, body=None):
    """Helper to create a basic domain config.

    Returns the response object.
    """
    request = Request.blank(self.uri_config, headers=[self.auth_header])
    request.method = 'POST'
    request.body = body
    return request.get_response(application)


  def test_config_post(self):
    body = '"foo":"bar"'
    response = self._create_config(body=body)
    self.assertEqual(response.status_int, 204)
    self.assertEqual(response.body, '')

    body = '{"foo":"bar", "clickcount":"0", "money":"0.0", "status":"0.0"}'
    request = Request.blank(self.uri_config, headers=[self.auth_header])
    response = request.get_response(application)
    self.assertEqual(response.body, body)


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


  def _test_c_post(self, uri, body):
    """Helper to actually test posting to /c, depending on uri and body."""
    request = Request.blank(uri, headers=[self.auth_header])
    request.method = 'POST'
    response = request.get_response(application)
    self.assertEqual(response.status_int, 200)
    self.assertEqual(response.body, body)


  def test_c_post_nocount(self):
    self._create_config()

    # all values should still be 0 on firstvisit == false
    uri = '/c?domain=' + self.domain + '&firstvisit=false&from=inside'
    body = '{ "clickcount":"0", "money":"0.0", "status":"0.0"}'
    self._test_c_post(uri, body)

    # all values should still be 0 on from == outside
    uri = '/c?domain=' + self.domain + '&firstvisit=true&from=outside'
    self._test_c_post(uri, body)


  def test_c_post_count(self):
    self._create_config()

    # this should count
    uri = '/c?domain=' + self.domain + '&firstvisit=true&from=inside'
    body = '{ "clickcount":"1", "money":"0.1", "status":"2e-05"}'
    self._test_c_post(uri, body)

    # this should count again
    body = '{ "clickcount":"2", "money":"0.2", "status":"4e-05"}'
    self._test_c_post(uri, body)


if __name__ == '__main__':
    unittest.main()
