import requests

from app.search.suggest.base import BaseSuggestionEngine


class BingSuggestionEngine(BaseSuggestionEngine):
    """
    Suggestion engine that returns results from Bing's search suggestions API.
    """
    def fetch(self, query):
        url = 'https://api.bing.com/osjson.aspx'
        params = {
            'query': query
        }
        response = requests.get(url, params)
        return response.json()

    def sanitize(self, results):
        """
        Normalizes an OpenSearch response that looks like:

        ['original query', ['list of', 'suggestions']]
        """
        return results[1]
