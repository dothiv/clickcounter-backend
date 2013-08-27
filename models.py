# app models
from google.appengine.ext import ndb

from settings import EUR_INCREMENT, EUR_TOTAL


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


  def get_json(self):
    """Converts the field data into proper JSON."""
    return '{%s "clickcount":"%s", "money":"%s", "status":"%s"}' % (
        self.content + ',' if self.content else '',
        self.clickcount, self.money, self.status
    )


  def increment_counter(self):
    """Increments clickcount, money and status."""
    self.clickcount += 1
    self.money += EUR_INCREMENT
    self.status = (self.money * 100) / EUR_TOTAL
    self.put()
