# app settings
import os, jinja2
import ConfigParser
import random, string

# secret to use for HTTP Basic Auth (/config)
AUTH_SECRET = ''.join(random.choice(string.lowercase) for i in range(10))
config = ConfigParser.RawConfigParser()
try:
  config.read('authenticationSecret.cfg')
  AUTH_SECRET = config.get('Authentication', 'secret')
except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
  pass

# how many EUR to increment on click; added to field 'money'
EUR_INCREMENT = 0.001

# number of clicks in past stretches
ALREADY_CLICKED = 0

# money already raised from past stretches
ALREADY_DONATED = 0

# budget available in current stretch; used to calculate status
EUR_GOAL = 50000

# project root directory
PROJECT_DIR = os.path.dirname(__file__)

# template directory
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'templates')

# the template engine's environment
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'])
