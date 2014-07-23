# app models

from google.appengine.ext import ndb

class Domain(ndb.Model):
  """
  Models an individual domain entry with content, clickcount, money and
  status.
  """
  name = ndb.StringProperty(indexed=True, required=True)
  content = ndb.TextProperty()
  clickcount = ndb.IntegerProperty(default=0)

class Config(ndb.Model):
    """
    Model used to store arbitrary configuration data
    """
    key = ndb.StringProperty(indexed=True, required=True)
    value = ndb.StringProperty(required=True)
