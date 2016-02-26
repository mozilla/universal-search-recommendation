from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from recommendation.search.query.yahoo import YahooQueryEngine
from recommendation.tests.memcached import mock_memcached


QUERY = 'loveland'
MOCK_RESPONSE = {
    'bossresponse': {
        'web': {
            'count': '2',
            'start': '0',
            'results': [
                {
                    'abstract': 'Welcome to <b>Loveland</b> Ski Area Near...',
                    'url': 'http://skiloveland.com/',
                    'title': '<b>Loveland</b> Ski Area :: Colorado Ski...',
                    'date': '',
                    'dispurl': 'ski<b>loveland</b>.com',
                    'clickurl': 'http://skiloveland.com/'
                },
                {
                    'abstract': 'The City of <b>Loveland</b> is the Home...',
                    'url': 'https://en.wikipedia.org/wiki/Loveland,_Colorado',
                    'title': '<b>Loveland</b>, Colorado - Wikipedia',
                    'date': '',
                    'dispurl': 'https://en.wikipedia.org/wiki/<b>Loveland...',
                    'clickurl': 'https://en.wikipedia.org/wiki/Loveland...'
                }
            ],
            'totalresults': '2'
        },
        'responsecode': '200'
    }
}


class TestYahooClassifier(TestCase):
    def setUp(self):
        self.instance = YahooQueryEngine('')

    def test_oauth_url(self):
        url = self.instance._oauth_url(QUERY)
        url_parsed = urlparse(url)
        query_string = parse_qs(url_parsed.query)
        ok_(url.startswith(YahooQueryEngine.url))
        ok_(len(query_string['oauth_body_hash']))
        ok_(len(query_string['oauth_nonce']))
        ok_(len(query_string['oauth_signature']))
        ok_(len(query_string['oauth_timestamp']))
        ok_(len(query_string['oauth_version']))
        eq_(query_string['q'][0], QUERY)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @responses.activate
    def test_fetch(self):
        responses.add(responses.GET, YahooQueryEngine.url,
                      json=MOCK_RESPONSE, status=200)
        response_cold = self.instance.fetch(QUERY)
        response_warm = self.instance.fetch(QUERY)
        ok_(not response_cold.from_cache)
        ok_(response_warm.from_cache)
        eq_(response_cold.cache_key, response_warm.cache_key)
        eq_(response_cold, response_warm, MOCK_RESPONSE)

    @patch('recommendation.memorize.memcached', mock_memcached)
    @responses.activate
    def test_sanitize_response(self):
        responses.add(responses.GET, YahooQueryEngine.url,
                      json=MOCK_RESPONSE, status=200)
        results = self.instance.fetch(QUERY)
        sanitized = self.instance.sanitize_response(results)
        eq_(type(sanitized), list)
        eq_(sanitized[0], MOCK_RESPONSE['bossresponse']['web']['results'][0])
