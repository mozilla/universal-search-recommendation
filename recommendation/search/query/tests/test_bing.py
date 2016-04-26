import json
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from recommendation.search.query.bing import BingQueryEngine
from recommendation.tests.memcached import mock_memcached


QUERY = 'mozilla'
MOCK_RESULT = {
    '__metadata': {
        'uri': ('https://api.datamarket.azure.com/Data.ashx/Bing/Search/Web'
                '?Query=\'mozilla\'&$skip=1&$top=1'),
        'type': 'WebResult'
    },
    'ID': 'abcdefghijklmnopqrstuvwxyz0123456',
    'Title': 'We\'re building a better Internet — Mozilla',
    'Description': 'Did you know? Mozilla — the maker of Firefox — fights...',
    'DisplayUrl': 'https://www.mozilla.org',
    'Url': 'https://www.mozilla.org/en-US/'
}
MOCK_RESPONSE = {
    'd': {
        '__next': '',
        'results': [
            MOCK_RESULT,
            MOCK_RESULT
        ]
    }
}


class TestBingClassifier(TestCase):
    def setUp(self):
        self.instance = BingQueryEngine('')

    @patch('recommendation.memorize.memcached', mock_memcached)
    @responses.activate
    def test_fetch(self):
        def request_callback(request):
            eq_(parse_qs(urlparse(request.url).query)['Adult'], ['Strict'])
            return 200, {}, json.dumps(MOCK_RESPONSE)

        responses.add_callback(responses.GET, BingQueryEngine.url,
                               callback=request_callback)
        response_cold = self.instance.fetch(QUERY)
        response_warm = self.instance.fetch(QUERY)
        ok_(not response_cold.from_cache)
        ok_(response_warm.from_cache)
        eq_(response_cold.cache_key, response_warm.cache_key)
        eq_(response_cold, response_warm, MOCK_RESPONSE)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @responses.activate
    def test_sanitize_response(self):
        responses.add(responses.GET, BingQueryEngine.url,
                      json=MOCK_RESPONSE, status=200)
        results = self.instance.fetch(QUERY)
        sanitized = self.instance.sanitize_response(results)
        eq_(type(sanitized), list)
        eq_(sanitized[0], MOCK_RESPONSE['d']['results'][0])

    def test_get_result_abstract(self):
        eq_(self.instance.get_result_abstract(MOCK_RESULT),
            MOCK_RESULT['Description'])

    def test_get_result_title(self):
        eq_(self.instance.get_result_title(MOCK_RESULT),
            MOCK_RESULT['Title'])

    def test_get_result_url(self):
        eq_(self.instance.get_result_url(MOCK_RESULT),
            MOCK_RESULT['Url'])
