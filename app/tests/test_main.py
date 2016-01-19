from urllib.parse import urlencode

from flask.ext.testing import TestCase
from mock import patch
from nose.tools import eq_

from app.main import application
from app.memorize import CacheMissError


QUERY = 'frend'
RESULTS = {
    'hello': 'frend'
}
EXCEPTION_ARGS = ['args']
EXCEPTION = RuntimeError(*EXCEPTION_ARGS)


class TestApp(TestCase):
    debug = False

    def create_app(self):
        app = application
        app.config['DEBUG'] = self.debug
        return app

    def _get(self, path):
        return self.client.get(path)

    def _query(self, query):
        url = '/?%s' % urlencode({
            'q': query
        })
        return self._get(url)

    def test_no_query(self):
        eq_(self._get('/').status_code, 400)

    @patch('app.search.recommendation.SearchRecommendation.__init__')
    def test_cache_miss(self, mock_recommendation):
        mock_recommendation.side_effect = CacheMissError
        response = self._query(QUERY)
        eq_(response.status_code, 202)
        eq_(response.json, {})

    @patch('app.search.recommendation.SearchRecommendation.do_search')
    def test_exception(self, mock_do_search):
        mock_do_search.side_effect = EXCEPTION
        response = self._query(QUERY)
        eq_(response.status_code, 500)
        eq_(response.json, {})

    @patch('app.search.recommendation.SearchRecommendation.do_search')
    def test_cache_hit(self, mock_do_search):
        mock_do_search.return_value = RESULTS
        eq_(self._query(QUERY).status_code, 200)
        eq_(self._query(QUERY).json, RESULTS)


class TestAppDebug(TestApp):
    debug = True

    @patch('app.search.recommendation.SearchRecommendation.do_search')
    def test_exception(self, mock_do_search):
        mock_do_search.side_effect = EXCEPTION
        response = self._query(QUERY)
        exception_name = list(response.json.keys())[0]
        eq_(response.status_code, 500)
        eq_(exception_name, EXCEPTION.__class__.__name__)
        eq_(response.json[exception_name], EXCEPTION_ARGS)
