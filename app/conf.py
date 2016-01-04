from os import environ as env


DEBUG = env.get('RECOMMENDATION_ENV', 'development') == 'development'
HOST = env.get('RECOMMENDATION_HOST', '0.0.0.0')
PORT = env.get('RECOMMENDATION_PORT', 5000)

MEMCACHED_HOST = env.get('MEMCACHED_HOST', '127.0.0.1')

YAHOO_OAUTH_KEY = env.get('YAHOO_OAUTH_KEY')
YAHOO_OAUTH_SECRET = env.get('YAHOO_OAUTH_SECRET')
