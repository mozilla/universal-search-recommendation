from os import environ as env


KEY_PREFIX = env.get('RECOMMENDATION_KEY_PREFIX', 'query_')

DEBUG = env.get('RECOMMENDATION_ENV', 'development') == 'development'
HOST = env.get('RECOMMENDATION_HOST', '0.0.0.0')
PORT = env.get('RECOMMENDATION_PORT', 5000)

CELERY_BROKER_URL = env.get('CELERY_BROKER_URL', 'redis://redis:6379/0')

MEMCACHED_HOST = env.get('MEMCACHED_HOST', 'memcached:11211')

EMBEDLY_API_KEY = env.get('EMBEDLY_API_KEY', '')

YAHOO_OAUTH_KEY = env.get('YAHOO_OAUTH_KEY', '')
YAHOO_OAUTH_SECRET = env.get('YAHOO_OAUTH_SECRET', '')
