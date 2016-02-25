import time
from urllib.parse import quote_plus

import oauth2
import requests

from recommendation import conf
from recommendation.memorize import memorize
from recommendation.search.query.base import BaseQueryEngine


class YahooQueryEngine(BaseQueryEngine):
    """
    Query engine that returns results from Yahoo's BOSS API.
    """
    url = 'http://yboss.yahooapis.com/ysearch/web'

    def _oauth_url(self, query):
        consumer = oauth2.Consumer(key=conf.YAHOO_OAUTH_KEY,
                                   secret=conf.YAHOO_OAUTH_SECRET)
        params = {
            'format': 'json',
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': str(int(time.time())),
            'oauth_version': '1.0',
            'q': quote_plus(query)
        }
        request = oauth2.Request(method='GET', url=self.url, parameters=params)
        request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(),
                             consumer, None)
        return request.to_url()

    @memorize(prefix='yahoo')
    def fetch(self, query):
        return requests.get(self._oauth_url(query)).json()

    def sanitize_response(self, results):
        return results['bossresponse']['web']['results']
