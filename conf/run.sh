#!/bin/bash

cd $(dirname $0)
case "$1" in
    web)
        echo "Starting Web Server"
        exec ./web.sh
        ;;
    worker)
        echo "Starting Celery Worker"
        exec ./worker.sh
        ;;
    test)
        echo "Running Tests"
        cd ..
        flake8 . --exclude=./recommendation/views/data/dummy.py
        RECOMMENDATION_TESTING=true nosetests
        ;;
    *)
        echo "Usage: $0 {web|worker|test}"
        exit 1
esac
