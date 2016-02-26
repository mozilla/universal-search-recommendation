from urllib.parse import urlencode

from mock import patch
from nose.tools import eq_, ok_

from recommendation.cors import cors_headers
from recommendation.tests.memcached import mock_memcached
from recommendation.tests.util import AppTestCase


KEY = 'query_key'
QUERY = 'frend'
RESULTS = {
    'hello': 'frend'
}
EXCEPTION_ARGS = ['args']
EXCEPTION = RuntimeError(*EXCEPTION_ARGS)


@patch('recommendation.tasks.task_recommend.memcached', mock_memcached)
class TestMain(AppTestCase):
    debug = False

    def tearDown(self):
        mock_memcached.flush_all()

    def _get(self, path):
        return self.client.get(path)

    def _query(self, query):
        url = '/?%s' % urlencode({
            'q': query
        })
        return self._get(url)

    def test_cors(self):
        headers = [
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Origin',
        ]
        ok_(all([header not in dict(self.app.response_class().headers).keys()
                 for header in headers]))
        cors_response = cors_headers(self.app.response_class())
        ok_(all([header in dict(cors_response.headers).keys()
                 for header in headers]))

    def test_no_query(self):
        eq_(self._get('/').status_code, 400)

    @patch('recommendation.tasks.task_recommend.memcached.get')
    def test_exception(self, mock_get):
        mock_get.side_effect = EXCEPTION
        response = self._query(QUERY)
        eq_(response.status_code, 500)
        eq_(response.json, {})

    @patch('recommendation.tasks.task_recommend.memcached.get')
    def test_cache_hit(self, mock_get):
        mock_get.return_value = RESULTS
        eq_(self._query(QUERY).status_code, 200)
        eq_(self._query(QUERY).json, RESULTS)

    @patch('recommendation.tasks.task_recommend.memcached.get')
    @patch('recommendation.tasks.task_recommend.recommend.delay')
    def test_cache_miss(self, mock_delay, mock_get):
        mock_get.return_value = None
        eq_(self._query(QUERY).status_code, 202)
        eq_(mock_delay.call_count, 1)


class TestMainDebug(TestMain):
    debug = True

    @patch('recommendation.tasks.task_recommend.memcached.get')
    @patch('recommendation.tasks.task_recommend.recommend.delay')
    def test_exception(self, mock_delay, mock_get):
        mock_get.side_effect = EXCEPTION
        response = self._query(QUERY)
        exception_name = list(response.json.keys())[0]
        eq_(response.status_code, 500)
        eq_(exception_name, EXCEPTION.__class__.__name__)
        eq_(response.json[exception_name], EXCEPTION_ARGS)
