from urllib.parse import urlencode, urlparse

import requests

from recommendation import conf
from recommendation.memorize import memorize
from recommendation.search.classification.base import BaseClassifier
from recommendation.util import image_url


class BaseEmbedlyClassifier(BaseClassifier):
    """

    """
    api_url = 'https://api.embed.ly/1/extract'

    def is_match(self, best_result, all_results):
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
        api_data = self._api_response(self.best_result['url'])
        favicon_url = self._get_url(api_data)
        if not favicon_url:
            return {}
        return {
            'color': self._get_color(api_data),
            'url': image_url(favicon_url, width=32, height=32),
        }


class WikipediaClassifier(BaseEmbedlyClassifier):
    """
    Classifier that adds image and title data about Wikipedia articles from
    Embedly:

    image.height - an int representing the height of the image in pixels.
    image.url - a string representing the URL to the image.
    image.width - an int representing the width of the image in pixels.
    title - a string representing the title of the Wikipedia article.
    """
    LOOK_AT = 5
    type = 'wikipedia'

    def __init__(self, best_result, all_results):
        self.wikipedia_url = None
        super(WikipediaClassifier, self).__init__(best_result, all_results)

    def is_match(self, best_result, all_results):
        """
        Matches if one of the first `self.LOOK_AT` results is a Wikipedia
        article.
        """
        if self._get_wikipedia_url():
            return True
        return False

    def _get_wikipedia_url(self):
        """
        Inspects each of the first `self.LOOK_AT` results in the full result
        set. If any of them appear to be from Wikipedia, return that result's
        URL and cache it for future invokations of this method on this
        instance.
        """
        if self.wikipedia_url:
            return self.wikipedia_url
        results = (self.all_results[:self.LOOK_AT] if len(self.all_results) >
                   self.LOOK_AT else self.all_results)
        for result in results:
            if self._is_wikipedia(result['url']):
                self.wikipedia_url = result['url']
                return result['url']
        return None

    def _is_wikipedia(self, url):
        """
        Parses the passed URL and returns True if it appears to be that of a
        Wikipedia article.
        """
        parsed = urlparse(url)
        return (parsed.netloc.endswith('wikipedia.org') and
                parsed.path.startswith('/wiki'))

    def _get_image(self, api_data):
        """
        Returns data about the article's key image, if it exists.
        """
        return api_data['images'][0]

    def _get_title(self, api_data):
        """
        Returns the article's title.
        """
        return api_data['title']

    def enhance(self):
        wikipedia_url = self._get_wikipedia_url()
        api_data = self._api_response(wikipedia_url)
        try:
            image_data = self._get_image(api_data)
            image = {k: image_data.get(k) for k in ['url', 'height', 'width']}
            image['url'] = image_url(image['url'])
        except (KeyError, IndexError):
            image = {}

        return {
            'image': image,
            'title': self._get_title(api_data),
            'url': wikipedia_url
        }
