#!/bin/sh
# Migrate, then serve. Render's free plan has no pre-deploy command, so the
# schema is brought up to date here, before gunicorn takes any traffic.
set -eu

python manage.py migrate --noinput
exec gunicorn pykaraoke.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
