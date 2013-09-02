# app models
from google.appengine.ext import ndb
from settings import EUR_INCREMENT, EUR_TOTAL
import os


class Domain(ndb.Model):
  """
  Models an individual domain entry with content, clickcount, money and
  status.
  """
  name = ndb.StringProperty(indexed=True, required=True)
  content = ndb.TextProperty()
  clickcount = ndb.IntegerProperty(default=0)
  money = ndb.FloatProperty(default=0.)
  status = ndb.FloatProperty(default=0.)


  def python_to_json_float(self, number):
    """Converts a Python (float) number to a string which can be used as
    number in a JSON snippet."""
    # convert to string with precision 8 and strip trailing 0s
    formatted_number = ('%.8f' % number).rstrip('0')

    # add trailing 0 if last char is a dot
    if formatted_number[-1]=='.':
      formatted_number +='0'

    return formatted_number


  def get_json(self):
    """Converts the field data into proper JSON."""
    return '{%s "clickcount":%s, "money":%s, "status":%s}' % (
        self.content + ',' if self.content else '',
        self.clickcount, self.python_to_json_float(self.money), self.python_to_json_float(self.status)
    )


  def increment_counter(self):
    """Increments clickcount, money and status."""
    self.clickcount += 1
    self.money += EUR_INCREMENT
    self.status = (self.money * 100) / EUR_TOTAL
    self.put()


class StaticFile(ndb.Model):
  name = ndb.StringProperty(indexed=True, required=True)
  content = ndb.TextProperty()
  content_type = ndb.StringProperty(required=True)

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