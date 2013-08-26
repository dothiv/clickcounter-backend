from google.appengine.ext import ndb

class Domain(ndb.Model):
    """Models an individual domain entry with clickcount and a content."""
    domain_name = ndb.StringProperty(indexed=True, required=True)
    content = ndb.StringProperty()
    clickcount = ndb.IntegerProperty(default=0)
