# app models
from google.appengine.ext import ndb
from settings import EUR_INCREMENT, EUR_GOAL
import os
import util


class Domain(ndb.Model):
  """
  Models an individual domain entry with content, clickcount, money and
  status.
  """
  name = ndb.StringProperty(indexed=True, required=True)
  content = ndb.TextProperty()
  clickcount = ndb.IntegerProperty(default=0)
  money = ndb.FloatProperty(default=0.)

  def increment_counter(self):
    """Increments clickcount, money and status."""
    self.clickcount += 1
    self.money += EUR_INCREMENT
    self.put()

class UserData(ndb.Model):
  remote_addr = ndb.StringProperty()
  http_user_agent = ndb.StringProperty()
  referer = ndb.StringProperty()
  domain = ndb.StringProperty()
  date_time = ndb.DateTimeProperty(auto_now_add=True)

  @classmethod
  def add(cls, request, domain):
    user_data = cls(remote_addr=os.environ.get('REMOTE_ADDR',None),
      http_user_agent= request.headers.get('HTTP_USER_AGENT', None),
      referer = request.referer,
      domain=domain)
    user_data.put()
