from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from recommendation.search.classification.wikipedia import WikipediaClassifier
from recommendation.tests.memcached import mock_memcached


SLUG = 'Mozilla'
TITLE = 'Mozilla'
ABSTRACT = ' \n\tMozilla is a free-software community... \n\t'
API_URL = ('http://example.com/')
MOCK_RESPONSE = {
    'query': {
        'general': {},
        'pages': {
            '36754915': {
                'extract': ABSTRACT,
                'pageid': 36754915,
                'title': TITLE,
                'ns': 0
            }
        }
    },
    'batchcomplete': ''
}
EXPECTED_SANITIZED_RESPONSE = {
    'pageid': 36754915,
    'ns': 0,
    'title': TITLE,
    'extract': ABSTRACT
}


class TestWikipediaClassifier(TestCase):
    def tearDown(self):
        mock_memcached.flush_all()

    def _result(self, url):
        return {
            'url': url
        }

    def _classifier(self, url):
        return WikipediaClassifier(self._result(url))

    def _matches(self, url):
        return self._classifier(url).is_match(self._result(url))

    def test_is_match(self):
        eq_(self._matches('https://www.mozilla.com/en_US'), False)
        eq_(self._matches('https://www.mozilla.com/en_US/'), False)
        eq_(self._matches('https://wikipedia.org'), False)
        eq_(self._matches('https://wikipedia.org/'), False)
        eq_(self._matches('https://en.wikipedia.org/wiki/Mozilla'), True)
        eq_(self._matches('https://en.wikipedia.org/wiki/Mozilla/'), True)

    def test_api_url(self):
        classifier = self._classifier('https://en.wikipedia.org/wiki/Mozilla')
        expected = list(urlparse(
            'https://en.wikipedia.org/w/api.php?exintro=&explaintext=&titles=M'
            'ozilla&redirects=&prop=extracts&meta=siteinfo&action=query&format'
            '=json'
        ))
        actual = list(urlparse(classifier._api_url('Mozilla')))
        expected[4] = parse_qs(expected[4])
        actual[4] = parse_qs(actual[4])
        eq_(expected, actual)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.wikipedia.WikipediaClassifier'
           '._api_url')
    @responses.activate
    def test_api_response(self, mock_api_url):
        """
        Tests WikipediaClassifier._api_response by running it twice for the
        same slug and:

        * Asserting that the first is not returned from the cache, while the
          second is.
        * Asserting that the cache keys for each are the same.
        * Asserting that the response body matches the expected sanitized
          response.
        """
        mock_api_url.return_value = API_URL
        classifier = self._classifier(SLUG)
        responses.add(responses.GET, API_URL, json=MOCK_RESPONSE, status=200)
        response_cold = classifier._api_response(SLUG)
        response_warm = classifier._api_response(SLUG)
        ok_(not response_cold.from_cache)
        ok_(response_warm.from_cache)
        eq_(response_cold.cache_key, response_warm.cache_key)
        eq_(response_cold, response_warm, EXPECTED_SANITIZED_RESPONSE)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.wikipedia.WikipediaClassifier'
           '._api_url')
    @responses.activate
    def test_enhance(self, mock_api_url):
        """
        Tests that the slug, abstract, and title are appropriate sanitized
        by WikipediaClassifier.enhance.
        """
        mock_api_url.return_value = API_URL
        responses.add(responses.GET, API_URL, json=MOCK_RESPONSE, status=200)
        enhanced = self._classifier(SLUG).enhance()
        ok_(enhanced['abstract'] in ABSTRACT)
        eq_(enhanced['slug'], SLUG)
        eq_(enhanced['title'], TITLE)
