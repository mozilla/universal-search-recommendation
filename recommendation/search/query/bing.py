import requests

from recommendation import conf
from recommendation.memorize import memorize
from recommendation.search.query.base import BaseQueryEngine


class BingQueryEngine(BaseQueryEngine):
    """
    Query engine that returns results from Bing's web search API.
    """
    url = 'https://api.datamarket.azure.com/Bing/Search/Web'

    @memorize(prefix='bing')
    def fetch(self, query):
        auth = ('', conf.BING_ACCOUNT_KEY)
        params = {
            'Query': '\'%s\'' % query,
            '$top': 20,
            '$format': 'JSON'
        }
        return requests.get(self.url, auth=auth, params=params).json()

    def sanitize_response(self, results):
        return results['d']['results']

    def get_result_abstract(self, result):
        return result['Description']

    def get_result_title(self, result):
        return result['Title']

    def get_result_url(self, result):
        return result['Url']
