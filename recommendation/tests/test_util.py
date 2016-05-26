from urllib.parse import parse_qs, quote, urlparse

from flask import current_app
from nose.tools import eq_

from recommendation.tests.util import AppTestCase
from recommendation.util import image_url


DIMENSION = '64'
IMAGE = 'https://foo.bar/image.jpg'
EMBEDLY_BASE = 'https://i.embed.ly/'
EMBEDLY_IMAGE = '{}?url={}'.format(EMBEDLY_BASE, quote(IMAGE))


class TestImageUrl(AppTestCase):
    def _image_url(self, url, **kwargs):
        with current_app.app_context():
            url = image_url(url, **kwargs)
            parsed = urlparse(url) if url else None
            qs = parse_qs(parsed.query) if parsed else None
            return url, parsed, qs

    def test_none(self):
        url, parsed, qs = self._image_url(None)
        eq_(url, None)

    def test_formed(self):
        url, parsed, qs = self._image_url(IMAGE, width=DIMENSION,
                                          height=DIMENSION)
        eq_(IMAGE, qs['url'][0])
        eq_(DIMENSION, qs['width'][0])
        eq_(DIMENSION, qs['height'][0])

    def test_embedly(self):
        url = self._image_url(IMAGE)
        embedly_url = self._image_url(EMBEDLY_IMAGE)
        eq_(url, embedly_url)

    def test_embedly_no_url(self):
        url, parsed, qs = self._image_url(EMBEDLY_BASE)
        eq_(qs['url'][0], EMBEDLY_BASE)

    def test_embedly_empty_url(self):
        URL = '{}?url='.format(EMBEDLY_BASE)
        url, parsed, qs = self._image_url(URL)
        eq_(qs['url'][0], URL)
