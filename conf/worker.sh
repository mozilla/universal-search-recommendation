#!/usr/bin/env bash

exec celery worker --app=recommendation
