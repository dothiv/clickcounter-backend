# app decorators
import base64
from settings import AUTH_SECRET


def basic_auth(func):
  """Decorator to enforce HTTP Basic Auth"""
  def callf(request, *args, **kwargs):
    # parse the header to extract the password
    auth_header = request.request.headers.get('Authorization')
    if auth_header != None:
      try:
        secret = base64.b64decode(auth_header.split(' ')[1]).split(':')[1:]
        # join by colon after user:password split
        secret = ':'.join(secret)
        if secret == AUTH_SECRET:
          return func(request, *args, **kwargs)
      except IndexError:
        pass

    # default is to initiate basic auth dialog
    request.response.set_status(401, message="Authorization Required")
    request.response.headers['WWW-Authenticate'] = 'Basic realm="dothiv"'
  return callf
