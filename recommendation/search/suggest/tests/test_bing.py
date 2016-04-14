from unittest import TestCase
from unittest.mock import patch

import responses
from nose.tools import eq_, ok_

from recommendation.search.suggest.bing import BingSuggestionEngine
from recommendation.tests.memcached import mock_memcached


QUERY = 'original query'
RESULTS = [
    'list of',
    'suggestions'
]
RESPONSE = [
    QUERY,
    RESULTS
]


class TestBingSuggestionEngine(TestCase):
    def setUp(self):
        self.instance = BingSuggestionEngine(QUERY)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @responses.activate
    def test_fetch(self):
        responses.add(responses.GET, BingSuggestionEngine.url, json=RESPONSE,
                      status=200)
        results_cold = self.instance.fetch(QUERY)
        results_warm = self.instance.fetch(QUERY)
        ok_(not results_cold.from_cache)
        ok_(results_warm.from_cache)
        eq_(results_cold.cache_key, results_warm.cache_key)
        eq_(results_cold, results_warm, RESPONSE)

    def test_sanitize(self):
        eq_(self.instance.sanitize(RESPONSE), RESULTS)

    def test_sanitize_malformed_results(self):
        eq_(self.instance.sanitize({}), [QUERY])
