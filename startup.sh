#!/bin/bash
python manage.py collectstatic --noinput
gunicorn -b :$PORT --workers 2 --threads 4 credible.wsgi:application