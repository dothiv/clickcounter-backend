# app settings
import os, jinja2
import random, string

# We are currently in test mode, the funding phase has not started yet
# TODO: remove once we are live
TEST_MODE = True


def get_test_mode():
    return TEST_MODE


def set_test_mode(mode):
    global TEST_MODE
    TEST_MODE = mode


# how many EUR to increment on click; added to field 'money'
EUR_INCREMENT = 0.001

# number of clicks in past stretches
ALREADY_CLICKED = 0

# money already raised from past stretches
ALREADY_DONATED = 0

# budget available in current stretch; used to calculate status
EUR_GOAL = 50000

# threshold between visits in microseconds to count as individual visits
COUNT_THRESHOLD = 60 * 1000

# project root directory
PROJECT_DIR = os.path.dirname(__file__)

# template directory
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'templates')

# the template engine's environment
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'])


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
