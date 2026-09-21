"""Production settings.

DEBUG is off, every transport-security setting is on. This is what
`manage.py check --deploy` and the test suite are held against, so a
regression here fails loudly before it ships.
"""

from .base import *  # noqa: F403

DEBUG = False

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
