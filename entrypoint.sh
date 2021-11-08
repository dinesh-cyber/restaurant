#!/bin/sh


python3 manage.py migrate
python3 manage.py collectstatic --noinput
exec gunicorn reflex.wsgi:application --name reflex --bind 0.0.0.0:8000
