from urllib.parse import urlencode

import requests

from recommendation import conf
from recommendation.memorize import memorize
from recommendation.search.classification.base import BaseClassifier


class BaseEmbedlyClassifier(BaseClassifier):
    """

    """
    api_url = 'https://api.embed.ly/1/extract'

    def is_match(self, result):
        return True

    def _api_url(self, url):
        return '%s?%s' % (self.api_url, urlencode({
            'key': conf.EMBEDLY_API_KEY,
            'words': 20,
            'secure': 'true',
            'url': url
        }))

    @memorize(prefix='embedly')
    def _api_response(self, url):
        return requests.get(self._api_url(url)).json()


class FaviconClassifier(BaseEmbedlyClassifier):
    """
    Classifier that adds favicon data from Embedly:

    color - the most prominent color in the favicon, taking the form
        `[r, g, b]`, where `r`, `g`, and `b` are ints on a 0-255 scale
        representing the red, green, and blue values of that color.
    url - a URL to the favicon.
    """
    type = 'favicon'

    def _get_color(self, api_data):
        colors = api_data.get('favicon_colors', None)
        return colors[0]['color'] if colors else None

    def _get_url(self, api_data):
        return api_data.get('favicon_url', None)

    def enhance(self):
        api_data = self._api_response(self.result['url'])
        favicon_url = self._get_url(api_data)
        if not favicon_url:
            return {}
        return {
            'color': self._get_color(api_data),
            'url': favicon_url,
        }


class KeyImageClassifier(BaseEmbedlyClassifier):
    """
    Classifier that adds key image data from Embedly:

    height - an int representing the height of the image in pixels.
    url - a string representing the URL to the image.
    width - an int representing the width of the image in pixels.
    """
    type = 'keyimage'

    def _get_image(self, api_data):
        return api_data['images'][0]

    def enhance(self):
        api_data = self._api_response(self.result['url'])
        try:
            image_data = self._get_image(api_data)
            image = {k: image_data.get(k) for k in ['url', 'height', 'width']}
        except (KeyError, IndexError):
            image = {}
        return image
