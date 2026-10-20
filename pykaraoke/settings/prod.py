"""Production settings.

DEBUG is off, every transport-security setting is on. This is what
`manage.py check --deploy` and the test suite are held against, so a
regression here fails loudly before it ships.
"""

from .base import *  # noqa: F403

DEBUG = False

SECURE_SSL_REDIRECT = True
# Render's health probe calls over plain HTTP; a 301 there would mark the service down.
SECURE_REDIRECT_EXEMPT = [r"^health/$"]
# Render terminates TLS and forwards plain HTTP with X-Forwarded-Proto. Without this,
# request.is_secure() is False and the SSL redirect loops. Safe only because Render is the
# sole way in: a request that skips the proxy could forge this header.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
