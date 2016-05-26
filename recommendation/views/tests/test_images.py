from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlparse

import responses
from nose.tools import eq_, ok_
from requests import RequestException

from recommendation.tests.util import AppTestCase
from recommendation.views.images import EMBEDLY_RESIZE, make_embedly_url


MOCK_API_KEY = 'hifrend'
MOCK_CONTENT_TYPE = 'image/jpeg'
MOCK_FILE_CONTENTS = ['Hello', 'World']
MOCK_URL = 'https://foo.bar/image.jpg'


def MOCK_FILE():
    for piece in MOCK_FILE_CONTENTS:
        yield piece


class TestImageViews(AppTestCase):
    def _url(self, url, **kwargs):
        url = make_embedly_url(url, **kwargs)
        parsed = urlparse(url) if url else None
        qs = parse_qs(parsed.query) if parsed else None
        return url, parsed, qs

    def _proxy(self, **kwargs):
        response = self.client.get('/images?{}'.format(urlencode(kwargs)))
        return response

    @patch('recommendation.views.images.conf.EMBEDLY_API_KEY', MOCK_API_KEY)
    def test_embedly_url(self):
        url, parsed, qs = self._url(MOCK_URL)
        ok_(url.startswith(EMBEDLY_RESIZE))
        ok_(MOCK_API_KEY in qs['key'])
        ok_('true' in qs['compresspng'])
        ok_('false' in qs['animate'])

    def test_embedly_url_kwargs(self):
        WIDTH = ['64']  # Mimicking how parse_qs parses `width=64`
        url, parsed, qs = self._url(MOCK_URL, width=WIDTH, foo='bar')
        eq_(WIDTH, qs['width'])
        ok_('foo' not in qs)

    def test_no_url(self):
        response = self._proxy()
        eq_(response.status_code, 400)

    @patch('recommendation.views.images.requests.get')
    def test_request_exception(self, mock_get):
        mock_get.side_effect = RequestException
        response = self._proxy(url=MOCK_URL)
        eq_(response.status_code, 400)

    @responses.activate
    def test_request_bad_response(self):
        responses.add(responses.GET, EMBEDLY_RESIZE, status=500)
        response = self._proxy(url=MOCK_URL)
        eq_(response.status_code, 400)

    @patch('recommendation.views.images.stream_with_context')
    @responses.activate
    def test_ok(self, mock_get_stream):
        responses.add(responses.GET, EMBEDLY_RESIZE, status=200,
                      content_type=MOCK_CONTENT_TYPE)
        mock_get_stream.return_value = MOCK_FILE()
        response = self._proxy(url=MOCK_URL)
        headers = dict(response.headers)
        eq_(headers['Content-Type'], MOCK_CONTENT_TYPE)
        ok_('Cache-Control' in headers)
        eq_(response.data.decode('ASCII'), ''.join(MOCK_FILE_CONTENTS))
