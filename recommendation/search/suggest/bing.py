import requests

from recommendation.memorize import memorize
from recommendation.search.suggest.base import BaseSuggestionEngine


class BingSuggestionEngine(BaseSuggestionEngine):
    """
    Suggestion engine that returns results from Bing's search suggestions API.
    """
    url = 'https://api.bing.com/osjson.aspx'

    @memorize(prefix='bing')
    def fetch(self, query):
        params = {
            'query': query
        }
        response = requests.get(self.url, params)
        return response.json()

    def sanitize(self, results):
        """
        Normalizes an OpenSearch response that looks like:

        ['original query', ['list of', 'suggestions']]

        If the top result is equal to the top search suggestion, Bing sometimes
        tries to be helpful and returns full web search results. In that case,
        let's return a single-item array containing the original query.
        """
        try:
            return results[1]
        except KeyError:
            return [self.query]
