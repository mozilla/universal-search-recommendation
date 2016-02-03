from urllib.parse import urlencode
from unittest import TestCase

from flask.ext.testing import TestCase as FlaskTestCase
from mock import patch
from nose.tools import eq_

from app.main import application, recommend
from app.tests.memcached import mock_memcached


KEY = 'query_key'
QUERY = 'frend'
RESULTS = {
    'hello': 'frend'
}
EXCEPTION_ARGS = ['args']
EXCEPTION = RuntimeError(*EXCEPTION_ARGS)


@patch('app.main.memcached', mock_memcached)
class TestApp(FlaskTestCase):
    debug = False

    def tearDown(self):
        mock_memcached.flush_all()

    def create_app(self):
        app = application
        app.config['DEBUG'] = self.debug
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
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

    @patch('app.tests.memcached.mock_memcached.get')
    def test_exception(self, mock_get):
        mock_get.side_effect = EXCEPTION
        response = self._query(QUERY)
        eq_(response.status_code, 500)
        eq_(response.json, {})

    @patch('app.tests.memcached.mock_memcached.get')
    @patch('app.main.recommend.delay')
    def test_cache_hit(self, mock_delay, mock_get):
        mock_get.return_value = RESULTS
        eq_(self._query(QUERY).status_code, 200)
        eq_(self._query(QUERY).json, RESULTS)

    @patch('app.tests.memcached.mock_memcached.get')
    @patch('app.main.recommend.delay')
    def test_cache_miss(self, mock_delay, mock_get):
        mock_get.return_value = None
        eq_(self._query(QUERY).status_code, 202)
        eq_(mock_delay.call_count, 1)


class TestAppDebug(TestApp):
    debug = True

    @patch('app.main.memcached.get')
    @patch('app.main.recommend.delay')
    def test_exception(self, mock_delay, mock_get):
        mock_get.side_effect = EXCEPTION
        response = self._query(QUERY)
        exception_name = list(response.json.keys())[0]
        eq_(response.status_code, 500)
        eq_(exception_name, EXCEPTION.__class__.__name__)
        eq_(response.json[exception_name], EXCEPTION_ARGS)


@patch('app.main.memcached', mock_memcached)
class TestRecommendTask(TestCase):
    task = recommend

    @patch('app.search.recommendation.SearchRecommendation.do_search')
    def test_recommend(self, mock_do_search):
        mock_do_search.return_value = RESULTS
        results = self.task.apply(args=[QUERY, KEY]).get()
        eq_(results, RESULTS)
        eq_(mock_memcached.get(KEY), RESULTS)
