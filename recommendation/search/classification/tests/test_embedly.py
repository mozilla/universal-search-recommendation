from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from recommendation.search.classification.embedly import (
    BaseEmbedlyClassifier, FaviconClassifier, WikipediaClassifier)
from recommendation.tests.memcached import mock_memcached
from recommendation.tests.util import AppTestCase
from recommendation.util import image_url


MOCK_API_KEY = '0123456789abcdef'
MOCK_API_URL = 'http://example.com/api'
MOCK_RESULT_URL = 'https://www.mozilla.com/en_US'

MOCK_NOT_WIKIPEDIA_URL = MOCK_RESULT_URL
MOCK_WIKIPEDIA_URL = 'https://en.wikipedia.org/wiki/The_Martian_(Weir_novel)'

MOCK_NOT_WIKIPEDIA_RESULT = {'url': MOCK_NOT_WIKIPEDIA_URL}
MOCK_WIKIPEDIA_RESULT = {'url': MOCK_WIKIPEDIA_URL}

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
MOCK_WIKIPEDIA_RESPONSE = {
    'image': {
        'height': MOCK_RESPONSE['images'][0]['height'],
        'url': MOCK_RESPONSE['images'][0]['url'],
        'width': MOCK_RESPONSE['images'][0]['width']
    },
    'title': MOCK_RESPONSE['title'],
    'url': MOCK_RESPONSE['url']
}


class TestBaseEmbedlyClassifier(AppTestCase):
    classifier_class = BaseEmbedlyClassifier

    def tearDown(self):
        mock_memcached.flush_all()

    def _result(self, url):
        return {
            'url': url
        }

    def _classifier(self, url):
        result = self._result(url)
        return self.classifier_class(result, [result])

    def _api_url(self, url):
        return self._classifier(url)._api_url(self._result(url)['url'])

    @patch('recommendation.conf.EMBEDLY_API_KEY', MOCK_API_KEY)
    def test_api_url(self):
        api_url = self._api_url(MOCK_RESULT_URL)
        api_qs = parse_qs(urlparse(api_url).query)
        ok_(api_url.startswith(self.classifier_class.api_url))
        eq_(api_qs['key'][0], MOCK_API_KEY)
        eq_(api_qs['url'][0], MOCK_RESULT_URL)
        eq_(api_qs['secure'][0], 'true')

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.embedly.BaseEmbedlyClassifier'
           '._api_url')
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


class TestFaviconClassifier(TestBaseEmbedlyClassifier):
    classifier_class = FaviconClassifier

    def test_is_match(self):
        eq_(self._classifier(MOCK_RESULT_URL).is_match(MOCK_RESPONSE,
                                                       [MOCK_RESPONSE]), True)

    def test_get_color(self):
        eq_(self._classifier(MOCK_RESULT_URL)._get_color(MOCK_RESPONSE),
            MOCK_RESPONSE['favicon_colors'][0]['color'])

    def test_get_url(self):
        eq_(self._classifier(MOCK_RESULT_URL)._get_url(MOCK_RESPONSE),
            MOCK_RESPONSE['favicon_url'])

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.embedly.FaviconClassifier'
           '._api_url')
    @responses.activate
    def test_enhance(self, mock_api_url):
        mock_api_url.return_value = MOCK_API_URL
        responses.add(responses.GET, MOCK_API_URL, json=MOCK_RESPONSE,
                      status=200)
        enhanced = self._classifier(MOCK_RESULT_URL).enhance()
        eq_(enhanced['color'], MOCK_RESPONSE['favicon_colors'][0]['color'])
        eq_(enhanced['url'], image_url(
            MOCK_RESPONSE['favicon_url'], width=32, height=32))

    @patch('recommendation.search.classification.embedly.FaviconClassifier'
           '._api_response')
    @patch('recommendation.search.classification.embedly.FaviconClassifier'
           '._get_url')
    @responses.activate
    def test_enhance_no_url(self, mock_get_url, mock_api_response):
        mock_api_response.return_value = MOCK_RESPONSE
        mock_get_url.return_value = None
        enhanced = self._classifier(MOCK_RESULT_URL).enhance()
        eq_(enhanced, {})


class TestWikipediaClassifier(TestBaseEmbedlyClassifier):
    classifier_class = WikipediaClassifier

    @patch('recommendation.search.classification.embedly.WikipediaClassifier'
           '._get_wikipedia_url')
    def test_is_match(self, mock_get_wikipedia_url):
        classifier = self._classifier(MOCK_RESULT_URL)
        mock_get_wikipedia_url.return_value = True
        eq_(classifier.is_match({}, [{}]), True)
        mock_get_wikipedia_url.return_value = False
        eq_(classifier.is_match({}, [{}]), False)

    @patch(('recommendation.search.classification.embedly.WikipediaClassifier'
            '.LOOK_AT'), 1)
    def test_get_wikipedia_url_match(self):
        classifier = self._classifier(MOCK_RESULT_URL)
        classifier.all_results = [MOCK_WIKIPEDIA_RESULT,
                                  MOCK_NOT_WIKIPEDIA_RESULT]
        eq_(classifier._get_wikipedia_url(), MOCK_WIKIPEDIA_URL)

    @patch(('recommendation.search.classification.embedly.WikipediaClassifier'
            '.LOOK_AT'), 1)
    def test_get_wikipedia_url_not_match(self):
        classifier = self._classifier(MOCK_RESULT_URL)
        classifier.all_results = [MOCK_NOT_WIKIPEDIA_RESULT,
                                  MOCK_WIKIPEDIA_RESULT]
        eq_(classifier._get_wikipedia_url(), None)

    @patch(('recommendation.search.classification.embedly.WikipediaClassifier'
            '.LOOK_AT'), 1)
    @patch('recommendation.search.classification.embedly.WikipediaClassifier'
           '._is_wikipedia')
    def test_get_wikipedia_url_caches(self, mock_is_wikipedia):
        mock_is_wikipedia.return_value = True
        classifier = self._classifier(MOCK_RESULT_URL)
        classifier.all_results = [MOCK_WIKIPEDIA_RESULT]

        # When run once, _is_wikipedia is called appropriately.
        eq_(classifier._get_wikipedia_url(), classifier.all_results[0]['url'])
        eq_(mock_is_wikipedia.call_count, 1)

        # When run a second time, _is_wikipedia is not called, but the correct
        # value is still returned.
        eq_(classifier._get_wikipedia_url(), classifier.all_results[0]['url'])
        eq_(mock_is_wikipedia.call_count, 1)

    def test_is_wikipedia(self):
        classifier = self._classifier(MOCK_RESULT_URL)
        ok_(classifier._is_wikipedia(MOCK_WIKIPEDIA_URL))
        ok_(not classifier._is_wikipedia(MOCK_NOT_WIKIPEDIA_URL))

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.embedly.WikipediaClassifier'
           '._api_url')
    @responses.activate
    def test_enhance(self, mock_api_url):
        mock_api_url.return_value = MOCK_API_URL
        responses.add(responses.GET, MOCK_API_URL, json=MOCK_RESPONSE,
                      status=200)
        enhanced = self._classifier(MOCK_WIKIPEDIA_URL).enhance()
        MOCK_WIKIPEDIA_RESPONSE['image']['url'] = (
            image_url(MOCK_WIKIPEDIA_RESPONSE['image']['url']))
        eq_(enhanced, MOCK_WIKIPEDIA_RESPONSE)

    @patch('recommendation.search.classification.embedly.WikipediaClassifier'
           '._api_response')
    @patch('recommendation.search.classification.embedly.WikipediaClassifier'
           '._get_image')
    def test_enhance_no_images(self, mock_get_image, mock_api_response):
        mock_api_response.return_value = MOCK_RESPONSE
        mock_get_image.side_effect = KeyError
        enhanced = self._classifier(MOCK_RESULT_URL).enhance()
        eq_(enhanced['image'], {})
        eq_(enhanced['title'], MOCK_RESPONSE['title'])
