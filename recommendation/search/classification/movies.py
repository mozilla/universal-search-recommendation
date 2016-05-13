import re
from urllib.parse import ParseResult, urlencode, urlparse

import requests

from recommendation.memorize import memorize
from recommendation.search.classification.base import BaseClassifier


class MovieClassifier(BaseClassifier):
    """
    Classifier that is applied if the returned result is a Wikipedia article.
    Adds:

    abstract - an excerpt from the Wikipedia article.
    slug - the article's URL slug.
    title - the article's title.
    """
    api_url = 'http://www.omdbapi.com/'
    type = 'movie'
    title_match = '\/title\/([A-Za-z0-9]+)\/'

    def _get_imdb_id(self, all_results):
        """
        Gets an appropriate IMDb ID for the search result set.
        """
        for result in all_results:
            url = urlparse(result['url'])
            if self._url_is_imdb(url):
                return re.search(self.title_match, url.path).group(1)
        return None

    def _url_is_imdb(self, url):
        """
        Passed a ParseResult instance, returns True if the URL is that of a
        movie or TV show on IMDB.
        """
        if not isinstance(url, ParseResult):
            url = urlparse(url)
        return (url.netloc.endswith('imdb.com') and
                len(re.search(self.title_match, url.path).groups()) > 0)

    def is_match(self, best_result, all_results):
        """
        Matches if any result in the full set is an IMDB detail page.
        """
        for result in all_results:
            if self._url_is_imdb(result['url']):
                return True
        return False

    def _api_url(self, all_results):
        """
        Passed a set of results, determines the appropriate API URL.
        """
        return '%s?%s' % (self.api_url, urlencode({
            'i': self._get_imdb_id(all_results),
            'plot': 'short',
            'r': 'json',
        }))

    @memorize(prefix='omdb')
    def _api_response(self, all_results):
        """
        Passed a set of results, returns the parsed JSON for an appropriate API
        request for those results.
        """
        return requests.get(self._api_url(all_results)).json()

    def _stars(self, score, max_score):
        """
        Passed a score and maximum score, normalizes to a 0-5 scale.
        """
        return float(score) / float(max_score) * 5

    def _score(self, score, max_score):
        """
        Passed a score and maximum score, returns a dict containing both the
        raw score and a normalized one.
        """
        if score == 'N/A':
            return None
        return {
            'raw': float(score),
            'stars': self._stars(score, max_score)
        }

    def enhance(self):
        data = self._api_response(self.all_results)
        return {
            'is_movie': data.get('Type') == 'movie',
            'is_series': data.get('Type') == 'series',
            'title': data.get('Title'),
            'year': data.get('Year'),
            'plot': data.get('Plot'),
            'poster': data.get('Poster'),
            'rating': {
                'imdb': self._score(data.get('imdbRating'), 10),
                'metacritic': self._score(data.get('Metascore'), 100)
            },
            'imdb_url': 'http://www.imdb.com/title/%s/' % data.get('imdbID'),
            'genre': data.get('Genre'),
            'runtime': data.get('Runtime')
        }
