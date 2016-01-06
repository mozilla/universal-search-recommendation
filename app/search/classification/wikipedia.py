from urllib.parse import urlencode, urlunparse

import requests

from app.memorize import memorize
from app.search.classification.base import BaseClassifier


class WikipediaClassifier(BaseClassifier):
    """
    Classifier that is applied if the returned result is a Wikipedia article.
    Adds:

    abstract - an excerpt from the Wikipedia article.
    slug - the article's URL slug.
    title - the article's title.
    """
    type = 'wikipedia'

    def is_match(self, result):
        """
        It is a Wikipedia article if both the netloc ends with 'wikipedia.org'
        and the path starts with '/wiki'.
        """
        return (self.url.netloc.endswith('wikipedia.org') and
                self.url.path.startswith('/wiki'))

    def _api_url(self, page_title):
        """
        Constructs a URL to the Wikipedia API endpoint for an article with the
        passed page title.
        """
        endpoint = list(self.url)
        endpoint[2] = '/w/api.php'
        endpoint[4] = urlencode({
            'action': 'query',
            'exintro': '',
            'explaintext': '',
            'format': 'json',
            'meta': 'siteinfo',
            'prop': 'extracts',
            'redirects': '',
            'titles': page_title
        })
        return urlunparse(endpoint)

    @memorize(prefix='wikipedia')
    def _api_response(self, page_title):
        """
        Makes an API request to Wikipedia, fetching the extract for the article
        with the passed page title.

        https://www.mediawiki.org/wiki/API:Main_page
        """
        url = self._api_url(page_title)
        response = requests.get(url)
        return list(response.json()['query']['pages'].items())[0][1]

    def enhance(self):
        slug = self.url.path.replace('wiki/', '').strip('/')
        api_data = self._api_response(slug)
        return {
            'abstract': api_data['extract'].strip(' \n\t'),
            'slug': slug,
            'title': api_data['title']
        }
