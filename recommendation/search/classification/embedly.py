from urllib.parse import urlencode

import requests

from recommendation import conf
from recommendation.memorize import memorize
from recommendation.search.classification.base import BaseClassifier
from recommendation.search.classification.wikipedia import WikipediaClassifier


class EmbedlyClassifier(BaseClassifier):
    """
    Classifier that adds data about the result from Embedly:

    favicon.colors - a list of prominent colors used in the favicon, taking the
        form:
        {
            'color': [r, g, b],
            'weight': 0.4526367188
        }
        , where `rgb` are ints on a 0-255 scale representing the color, and
        weight is a float between 0 and 1 representing the prominence of the
        color in the image.
    favicon.url - a URL to the favicon.
    image - additional data about a key image on the page, taking the form:
        {
            'caption': caption,
            'height': h,
            'size': size,
            'url': url,
            'width': w
        }
        where `caption` is a string representing a prospective caption, `h` is
        an int representing the height of the image in pixels, `size` is an int
        representing the file size of the image in bytes, `url` is a string
        with the URL to the image, and `w` is the width of the image in pixels.
    """
    api_url = 'https://api.embed.ly/1/extract'
    type = 'embedly'

    def is_match(self, result):
        """
        Apply the enhancer if the result URL is either a top-level directory on
        a domain, or if it is a Wikipedia article.
        """
        path = self.url.path.strip('/')
        if path and '/' not in path:
            return True
        return WikipediaClassifier(result).is_match(result)

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

    def _get_image(self, api_data):
        return api_data.get('images')[0]

    def enhance(self):
        api_data = self._api_response(self.result['url'])
        try:
            image = self._get_image(api_data)
        except (KeyError, IndexError):
            image = None
        return {
            'favicon': {
                'colors': api_data.get('favicon_colors', None),
                'url': api_data.get('favicon_url', None)
            },
            'image': image
        }
