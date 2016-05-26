#!/usr/bin/env bash

exec uwsgi --wsgi-disable-file-wrapper --http :${PORT:-8000} --wsgi-file /app/recommendation/wsgi.py --master
