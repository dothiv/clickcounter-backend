# app settings
import os, jinja2

AUTH_SECRET = 'Aladdin:open sesame' # 'QWxhZGRpbjpvcGVuIHNlc2FtZQ=='
EUR_INCREMENT = 0.1
EUR_TOTAL = 500000

PROJECT_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = 'templates'
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATE_DIR),
    extensions=['jinja2.ext.autoescape'])
