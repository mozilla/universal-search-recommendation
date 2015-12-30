from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from app.search.classification.embedly import EmbedlyClassifier
from app.tests.memcached import mock_memcached


MOCK_API_KEY = '0123456789abcdef'
MOCK_API_URL = 'http://example.com/api'
MOCK_RESULT_URL = 'https://www.mozilla.com/en_US'

MOCK_RESPONSE = {
    'app_links': [],
    'authors': [],
    'cache_age': 84732,
    'content': '<p><i><b>The Martian</b></i></p>\n',
    'embeds': [],
    'entities': [
        {'count': 21, 'name': 'Watney'},
        {'count': 10, 'name': 'Hermes'},
        {'count': 10, 'name': 'NASA'}],
    'favicon_colors': [
        {'color': [247, 247, 247], 'weight': 0.4621582031},
        {'color': [26, 26, 26], 'weight': 0.1003417969}
    ],
    'favicon_url': 'https://www.example.com/favicon.png',
    'images': [
        {
            'caption': 'Hello frend.',
            'colors': [
                {'color': [45, 61, 69], 'weight': 0.6867675781},
                {'color': [83, 98, 102], 'weight': 0.2629394531}
            ],
            'entropy': 5.5492707414,
            'height': 100,
            'size': 6933,
            'url': 'https://www.example.com/image.png',
            'width': 200
        }
    ],
    'keywords': [
        {'name': 'watney', 'score': 155},
        {'name': 'mav', 'score': 80},
        {'name': 'hermes', 'score': 76},
    ],
    'language': 'English',
    'lead': None,
    'media': {},
    'offset': None,
    'original_url': 'https://en.wikipedia.org/wiki/The_Martian_(Andy_Weir)',
    'provider_display': 'en.wikipedia.org',
    'provider_name': 'Wikipedia',
    'provider_url': 'https://en.wikipedia.org',
    'published': None,
    'related': [],
    'safe': True,
    'title': 'The Martian (Weir novel)',
    'type': 'html',
    'url': 'https://en.wikipedia.org/wiki/The_Martian_(Weir_novel)'
}


class TestEmbedlyClassifier(TestCase):
    def tearDown(self):
        mock_memcached.flush_all()

    def _result(self, url):
        return {
            'url': url
        }

    def _classifier(self, url):
        return EmbedlyClassifier(self._result(url))

    def _matches(self, url):
        return self._classifier(url).is_match(self._result(url))

    def _api_url(self, url):
        return self._classifier(url)._api_url(self._result(url)['url'])

    def test_is_match(self):
        eq_(self._matches('https://www.mozilla.com'), False)
        eq_(self._matches('https://www.mozilla.com/'), False)
        eq_(self._matches('https://www.mozilla.com/en_US'), True)
        eq_(self._matches('https://www.mozilla.com/en_US/'), True)
        eq_(self._matches('https://wikipedia.org'), False)
        eq_(self._matches('https://wikipedia.org/'), False)
        eq_(self._matches('https://en.wikipedia.org/wiki/Mozilla'), True)
        eq_(self._matches('https://en.wikipedia.org/wiki/Mozilla/'), True)

    @patch('app.conf.EMBEDLY_API_KEY', MOCK_API_KEY)
    def test_api_url(self):
        api_url = self._api_url(MOCK_RESULT_URL)
        api_qs = parse_qs(urlparse(api_url).query)
        ok_(api_url.startswith(EmbedlyClassifier.api_url))
        eq_(api_qs['key'][0], MOCK_API_KEY)
        eq_(api_qs['url'][0], MOCK_RESULT_URL)
        eq_(api_qs['secure'][0], 'true')

    @patch('app.memorize.memcached', mock_memcached)
    @patch('app.search.classification.embedly.EmbedlyClassifier._api_url')
    @responses.activate
    def test_api_response(self, mock_api_url):
        mock_api_url.return_value = MOCK_API_URL
        classifier = self._classifier(MOCK_RESULT_URL)
        responses.add(responses.GET, MOCK_API_URL, json=MOCK_RESPONSE,
                      status=200)
        response_cold = classifier._api_response(MOCK_RESULT_URL)
        response_warm = classifier._api_response(MOCK_RESULT_URL)
        ok_(not response_cold.from_cache)
        ok_(response_warm.from_cache)
        eq_(response_cold.cache_key, response_warm.cache_key)
        eq_(response_cold, response_warm, MOCK_RESPONSE)

    @patch('app.memorize.memcached', mock_memcached)
    @patch('app.search.classification.embedly.EmbedlyClassifier._api_url')
    @responses.activate
    def test_enhance(self, mock_api_url):
        mock_api_url.return_value = MOCK_API_URL
        responses.add(responses.GET, MOCK_API_URL, json=MOCK_RESPONSE,
                      status=200)
        enhanced = self._classifier(MOCK_RESULT_URL).enhance()
        ok_(all(k in enhanced.keys() for k in ['image', 'favicon']))
        ok_(all(k in enhanced['favicon'].keys() for k in ['colors', 'url']))
        eq_(enhanced['image'], MOCK_RESPONSE['images'][0])
        eq_(enhanced['favicon']['colors'], MOCK_RESPONSE['favicon_colors'])
        eq_(enhanced['favicon']['url'], MOCK_RESPONSE['favicon_url'])

    @patch('app.search.classification.embedly.EmbedlyClassifier._api_response')
    @patch('app.search.classification.embedly.EmbedlyClassifier._get_image')
    def test_enhance_no_images(self, mock_get_image, mock_api_response):
        mock_api_response.return_value = MOCK_RESPONSE
        mock_get_image.side_effect = KeyError
        enhanced = self._classifier(MOCK_RESULT_URL).enhance()
        eq_(enhanced['image'], None)
