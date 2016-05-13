from copy import copy
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import responses
from nose.tools import eq_, ok_

from recommendation.search.classification.movies import MovieClassifier
from recommendation.tests.memcached import mock_memcached


IMDB_ID = 'tt0116756'
RESULT_IMDB = {
    'url': 'http://www.imdb.com/title/{}/?ref_=fn_al_tt_1'.format(IMDB_ID)
}
RESULT_NOT_IMDB = {
    'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
}

RESULTS_NO_IMDB = [
    RESULT_NOT_IMDB,
    RESULT_NOT_IMDB,
    RESULT_NOT_IMDB,
    RESULT_NOT_IMDB
]
RESULTS_IMDB_LAST = copy(RESULTS_NO_IMDB)
RESULTS_IMDB_LAST.append(RESULT_IMDB)
RESULTS_IMDB_FIRST = copy(RESULTS_IMDB_LAST)
RESULTS_IMDB_FIRST.reverse()

MOCK_API_URL = 'http://www.slashfilm.com/kazaam-oral-history/'
MOCK_RESPONSE = {
    'Title': 'Kazaam',
    'Year': '1996',
    'Rated': 'PG',
    'Released': '17 Jul 1996',
    'Runtime': '93 min',
    'Genre': 'Comedy, Family, Fantasy',
    'Director': 'Paul Michael Glaser',
    'Writer': 'Paul Michael Glaser (story), Christian Ford (screenplay)...',
    'Actors': 'Shaquille O\'Neal, Francis Capra, Ally Walker, James Acheson',
    'Plot': 'Being a lone young boy in the...',
    'Language': 'English',
    'Country': 'USA',
    'Awards': 'N/A',
    'Poster': 'http://ia.media-imdb.com/images/M/MV5Q@@._V1_SX300.jpg',
    'Metascore': '24',
    'imdbRating': '2.8',
    'imdbVotes': '19,463',
    'imdbID': 'tt0116756',
    'Type': 'movie',
    'Response': 'True'
}


class TestMovieClassifier(TestCase):
    def setUp(self):
        self.classifier = MovieClassifier(RESULT_IMDB, [])

    def tearDown(self):
        mock_memcached.flush_all()

    def test_get_imdb_id(self):
        eq_(self.classifier._get_imdb_id(RESULTS_NO_IMDB), None)
        eq_(self.classifier._get_imdb_id(RESULTS_IMDB_LAST), IMDB_ID)
        eq_(self.classifier._get_imdb_id(RESULTS_IMDB_FIRST), IMDB_ID)

    def test_url_is_imdb(self):
        ok_(self.classifier._url_is_imdb(RESULT_IMDB['url']))
        ok_(not self.classifier._url_is_imdb(RESULT_NOT_IMDB['url']))

    def test_is_match(self):
        ok_(self.classifier.is_match({}, RESULTS_IMDB_FIRST))
        ok_(self.classifier.is_match({}, RESULTS_IMDB_LAST))
        ok_(not self.classifier.is_match({}, RESULTS_NO_IMDB))

    def test_api_url(self):
        url = self.classifier._api_url(RESULTS_IMDB_LAST)
        qs = parse_qs(urlparse(url).query)
        ok_(url.startswith(MovieClassifier.api_url))
        ok_(IMDB_ID in qs['i'])
        ok_('short' in qs['plot'])
        ok_('json' in qs['r'])

    def test_stars(self):
        eq_(self.classifier._stars(0, 5), 0.0)
        eq_(self.classifier._stars(3, 5), 3.0)
        eq_(self.classifier._stars(5, 5), 5.0)
        eq_(self.classifier._stars(2.5, 10), 1.25)
        eq_(self.classifier._stars(6.5, 10), 3.25)
        eq_(self.classifier._stars(9, 10), 4.5)
        eq_(self.classifier._stars(40, 100), 2.0)

    def test_score(self):
        eq_(self.classifier._score('N/A', 5), None)
        eq_(self.classifier._score('0', 5), {'raw': 0.0,  'stars': 0.0})
        eq_(self.classifier._score('4.25', 5), {'raw': 4.25,  'stars': 4.25})
        eq_(self.classifier._score('85', 100), {'raw': 85.0,  'stars': 4.25})
        eq_(self.classifier._score('50.0', 50), {'raw': 50.0,  'stars': 5.0})

    @patch('recommendation.memorize.memcached', mock_memcached)
    @patch('recommendation.search.classification.movies.MovieClassifier'
           '._api_url')
    @responses.activate
    def test_api_response(self, mock_api_url):
        mock_api_url.return_value = MOCK_API_URL
        responses.add(responses.GET, MOCK_API_URL, json=MOCK_RESPONSE,
                      status=200)
        classifier = MovieClassifier(RESULT_IMDB, RESULTS_IMDB_FIRST)
        response_cold = classifier._api_response(RESULTS_IMDB_FIRST)
        response_warm = classifier._api_response(RESULTS_IMDB_FIRST)
        ok_(not response_cold.from_cache)
        ok_(response_warm.from_cache)
        eq_(response_cold.cache_key, response_warm.cache_key)
        eq_(response_cold, response_warm, MOCK_RESPONSE)

    @patch('recommendation.search.classification.movies.MovieClassifier'
           '._api_response')
    def test_enhance(self, mock_api_response):
        mock_api_response.return_value = MOCK_RESPONSE
        enhanced = self.classifier.enhance()
        eq_(enhanced['is_movie'], True)
        eq_(enhanced['is_series'], False)
        eq_(enhanced['title'], MOCK_RESPONSE['Title'])
        eq_(enhanced['year'], MOCK_RESPONSE['Year'])
        eq_(enhanced['plot'], MOCK_RESPONSE['Plot'])
        eq_(enhanced['poster'], MOCK_RESPONSE['Poster'])
        eq_(enhanced['rating']['imdb']['stars'], 1.4)
        eq_(enhanced['rating']['imdb']['raw'], 2.8)
        eq_(enhanced['rating']['metacritic']['stars'], 1.2)
        eq_(enhanced['rating']['metacritic']['raw'], 24.0)
        eq_(enhanced['imdb_url'], 'http://www.imdb.com/title/tt0116756/')
        eq_(enhanced['genre'], MOCK_RESPONSE['Genre'])
        eq_(enhanced['runtime'], MOCK_RESPONSE['Runtime'])
