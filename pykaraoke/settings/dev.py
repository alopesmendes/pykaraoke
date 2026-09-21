"""Local development settings.

DEBUG is on, secure-cookie and HTTPS-only settings are off: a plain
`http://localhost` dev server has no TLS to redirect to or protect a
cookie over.
"""

from .base import *  # noqa: F403

DEBUG = True

SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
