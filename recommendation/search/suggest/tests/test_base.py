from unittest import TestCase

from mock import patch
from nose.tools import eq_, ok_

from recommendation.search.suggest.base import BaseSuggestionEngine
from recommendation.tests.memcached import mock_memcached


QUERY = ''
RESULTS = [
    {
        'test': 'results'
    }
]


class TestBaseSuggestionEngine(TestCase):
    def setUp(self):
        self.instance = BaseSuggestionEngine(QUERY)

    def test_init(self):
        eq_(self.instance.query, QUERY)

    def test_fetch(self):
        with self.assertRaises(NotImplementedError):
            self.instance.fetch(self.instance.query)

    def test_sanitize(self):
        eq_(self.instance.sanitize(RESULTS), RESULTS)

    @patch('recommendation.search.suggest.base.BaseSuggestionEngine.fetch')
    @patch('recommendation.memorize.memcached', mock_memcached)
    def test_search(self, mock_fetch):
        mock_fetch.return_value = RESULTS
        results_cold = self.instance.search(QUERY)
        results_warm = self.instance.search(QUERY)
        ok_(not results_cold.from_cache)
        ok_(results_warm.from_cache)
        eq_(results_cold.cache_key, results_warm.cache_key)
        eq_(results_cold, results_warm, RESULTS)
