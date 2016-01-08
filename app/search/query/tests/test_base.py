from unittest import TestCase
from unittest.mock import patch

from nose.tools import eq_, ok_

from app.search.query.base import BaseQueryEngine
from app.tests.memcached import mock_memcached


QUERY = 'loveland'
MOCK_RESULTS = [
    {
        'abstract': 'Welcome to <b>Loveland</b> Ski Area Near to the...',
        'title': '<b>Loveland</b> Ski Area :: Colorado Ski Snowboarding...',
        'url': 'http://skiloveland.com/'
    },
    {
        'abstract': 'Loveland Ski Area is a ski area in the western United...',
        'title': 'Loveland Ski Area - Wikipedia, the free encyclopedia',
        'url': 'https://en.wikipedia.org/wiki/Loveland_Ski_Area'
    }
]
MOCK_RESULT_SANITIZED = {
    'abstract': 'Welcome to Loveland Ski Area Near to the...',
    'title': 'Loveland Ski Area :: Colorado Ski Snowboarding...',
    'url': 'http://skiloveland.com/'
}


class TestBaseQueryEngine(TestCase):
    def setUp(self):
        self.instance = BaseQueryEngine('')

    def test_fetch(self):
        with self.assertRaises(NotImplementedError):
            self.instance.fetch(QUERY)

    def test_sanitize_response(self):
        eq_(self.instance.sanitize_response(MOCK_RESULTS), MOCK_RESULTS)

    def test_get_best_result(self):
        eq_(self.instance.get_best_result(MOCK_RESULTS), MOCK_RESULTS[0])

    @patch('app.search.query.base.BaseQueryEngine.get_result_abstract')
    @patch('app.search.query.base.BaseQueryEngine.get_result_title')
    @patch('app.search.query.base.BaseQueryEngine.get_result_url')
    def test_sanitize_result(self, *args):
        result = self.instance.sanitize_result(MOCK_RESULTS[0])
        ok_(all(k in result.keys() for k in ['abstract', 'title', 'url']))
        ok_(all([mock.call_count == 1 for mock in args]))

    def test_strip_html(self):
        eq_(self.instance._strip_html('This is not HTML'), 'This is not HTML')
        eq_(self.instance._strip_html('<b>This is HTML</b>'), 'This is HTML')
        eq_(self.instance._strip_html('This <b>is</b> HTML'), 'This is HTML')
        eq_(self.instance._strip_html('This <b><i>HTML</b></i>'), 'This HTML')
        eq_(self.instance._strip_html('This <b><i>HTML</i></b>'), 'This HTML')
        eq_(self.instance._strip_html('<b>This <i>HTML</i></b>'), 'This HTML')

    def test_get_result_title(self):
        eq_(self.instance.get_result_title(MOCK_RESULTS[0]),
            MOCK_RESULT_SANITIZED['title'])

    def test_get_result_url(self):
        eq_(self.instance.get_result_url(MOCK_RESULTS[0]),
            MOCK_RESULT_SANITIZED['url'])

    def test_get_result_abstract(self):
        eq_(self.instance.get_result_abstract(MOCK_RESULTS[0]),
            MOCK_RESULT_SANITIZED['abstract'])

    @patch('app.search.query.base.BaseQueryEngine.fetch')
    @patch('app.memorize.memcached', mock_memcached)
    def test_search(self, mock_fetch):
        mock_fetch.return_value = MOCK_RESULTS
        results_cold = self.instance.search(QUERY)
        results_warm = self.instance.search(QUERY)
        ok_(not results_cold.from_cache)
        ok_(results_warm.from_cache)
        eq_(results_cold.cache_key, results_warm.cache_key)
        eq_(results_cold, results_warm, MOCK_RESULT_SANITIZED)
