# app settings
import os, jinja2

# secret to use for HTTP Basic Auth (/config)
AUTH_SECRET = 'Aladdin:open sesame' # 'QWxhZGRpbjpvcGVuIHNlc2FtZQ=='

# how many EUR to increment on click; added to field 'money'
EUR_INCREMENT = 0.1

# total budget available; used to calculate status
EUR_TOTAL = 500000

# project root directory
PROJECT_DIR = os.path.dirname(__file__)

# template directory
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'templates')

# the template engine's environment
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'])
