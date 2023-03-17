#!/bin/bash

# Apply database migrations
python manage.py migrate --noinput

# Create superuser
python manage.py createsuperuser --email "$DJANGO_SUPERUSER_EMAIL" --noinput || true

python manage.py loaddata mydata.json

# Start uWSGI server
uwsgi --ini uwsgi.ini