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
    redirect_url = ndb.TextProperty()
    redirect_enabled = ndb.BooleanProperty(default=False)

class ClickcountDate(ndb.Model):
    """
    Stores the total click count for the given time
    """
    clickcount = ndb.IntegerProperty(default=0)
    time = ndb.DateTimeProperty(auto_now_add=True)


class Config(ndb.Model):
    """
    Model used to store arbitrary configuration data
    """
    key = ndb.StringProperty(indexed=True, required=True)
    value = ndb.StringProperty(required=True)
