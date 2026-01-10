#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate --noinput
gunicorn -b :$PORT --workers 2 --threads 4 credible.wsgi:application