# app settings
import os
import random, string

# how many EUR to increment on click; added to field 'money'
EUR_INCREMENT = 0.01

# number of clicks in past stretches
ALREADY_CLICKED = 34900

# money already raised from past stretches
ALREADY_DONATED = 34.90

# overall goal; used to calculate status
EUR_GOAL = 61801

# threshold between visits in microseconds to count as individual visits
COUNT_THRESHOLD = 60 * 1000

# project root directory
PROJECT_DIR = os.path.dirname(__file__)

def set_auth_secret(secret):
    """
    Sets the auth secret.
    """
    from models import Config
    secret_config = Config()
    secret_config.key = "auth_secret"
    secret_config.value = secret
    secret_config.put()
    return secret_config


def get_auth_secret():
    """
    Returns the secret required to update the click counter configuration.

    If no secret is configured, a random secret is generated and persisted.
    """
    from models import Config
    secret_config = Config.query(Config.key == "auth_secret").get()
    if not secret_config:
        secret_config = set_auth_secret(''.join(random.choice(string.lowercase) for i in range(10)))
    return secret_config.value
