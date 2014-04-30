from models import Domain
from google.appengine.api import memcache


def update_total_clicks():
    """
    Updates the memcached total clickcount value
    TODO: this should be replaced by a persisted total clickcount value, see https://trello.com/c/SDqocyuY
    """
    clicks = 0
    for domain in Domain.query():
        clicks = clicks + domain.clickcount
    memcache.set('clicks_total', clicks)
