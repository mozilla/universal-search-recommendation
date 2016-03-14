#!/usr/bin/env bash

exec uwsgi --http :${PORT:-8000} --wsgi-file /app/recommendation/wsgi.py --master
