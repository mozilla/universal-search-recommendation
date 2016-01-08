from unittest import TestCase

import responses
from mock import patch
from nose.tools import eq_, ok_

from app.search.suggest.bing import BingSuggestionEngine
from app.tests.memcached import mock_memcached


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

    @patch('app.memorize.memcached', mock_memcached)
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
