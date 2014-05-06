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


class Config(ndb.Model):
    """
    Model used to store arbitrary configuration data
    """
    key = ndb.StringProperty(indexed=True, required=True)
    value = ndb.StringProperty(required=True)
