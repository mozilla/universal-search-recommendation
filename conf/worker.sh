#!/bin/sh

exec celery worker --app=recommendation
