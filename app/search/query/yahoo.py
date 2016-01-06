import time
from urllib.parse import quote_plus

import oauth2
import requests

from app import conf
from app.search.query.base import BaseQueryEngine


class YahooQueryEngine(BaseQueryEngine):
    """
    Query engine that returns results from Yahoo's BOSS API.
    """
    def fetch(self, query):
        url = 'http://yboss.yahooapis.com/ysearch/web'
        consumer = oauth2.Consumer(key=conf.YAHOO_OAUTH_KEY,
                                   secret=conf.YAHOO_OAUTH_SECRET)
        params = {
            'format': 'json',
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0',
            'q': quote_plus(query)
        }
        request = oauth2.Request(method='GET', url=url, parameters=params)
        request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                             consumer, None)
        response = requests.get(request.to_url())
        return response.json()

    def sanitize_response(self, results):
        return results['bossresponse']['web']['results']
