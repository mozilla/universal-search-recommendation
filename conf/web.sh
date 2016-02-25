#!/usr/bin/env bash

<<<<<<< HEAD
uwsgi --http :${PORT:-8000} --wsgi-file ../app/main.py --master
=======
uwsgi --http :${PORT:-8000} --wsgi-file /app/recommendation/wsgi.py --master
>>>>>>> 579c385... fixup! WIP
