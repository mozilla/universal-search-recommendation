#!/usr/bin/env bash

uwsgi --http :8000 --wsgi-file /app/main.py --master
