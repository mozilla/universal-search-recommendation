import json
from time import time

from mock import MagicMock, patch
from nose.tools import eq_, ok_

from recommendation.mozlog.middleware import request_summary, request_timer
from recommendation.tests.util import AppTestCase


WITH_CLASSIFIERS = {
    'enhancements': {
        'hello': '',
        'frend': ''
    }
}
DUMMY = 'Hello, frend.'
REQUEST_PATH = 'recommendation.mozlog.middleware.request'


class TestMozLogMiddleware(AppTestCase):
    def _response(self, data=None, status_code=200, **kwargs):
        response = MagicMock()
        response.get_data.return_value = json.dumps(data or {})
        response.status_code = status_code
        return response

    def _request(self, args='hello', headers='world', path='/',
                 method='GET'):
        request = MagicMock()
        request.args.get.return_value = args
        request.headers.get.return_value = headers
        request.method = method
        request.path = path
        request.start_time = time()
        return request

    def _request_summary(self, request_args=None, response_args=None):
        request_args = request_args or {}
        response_args = response_args or {}
        with patch('recommendation.mozlog.middleware.current_app') as app:
            mock_request = self._request(**request_args)
            mock_response = self._response(**response_args)
            with patch(REQUEST_PATH, mock_request):
                request_summary(mock_response)
            return (app.logger.info.call_args[1]['extra'], mock_request,
                    mock_response)

    def _query(self, query):
        return self._request_summary(request_args={
            'args': query
        })

    def _predicates(self, query):
        return self._query(query)[0]['predicates']

    @patch(REQUEST_PATH)
    def test_request_timer(self, mock_request):
        request_timer()
        ok_(type(mock_request.start_time), float)

    def test_request_summary_headers(self):
        output, req, res = self._request_summary(request_args={
            'headers': DUMMY
        })
        eq_(output['agent'], DUMMY)
        eq_(output['lang'], DUMMY)

    def test_request_summary_errno_400(self):
        output, req, res = self._request_summary(response_args={
            'status_code': 400
        })
        eq_(output['errno'], 400)

    def test_request_summary_errno_200(self):
        output, req, res = self._request_summary(response_args={
            'status_code': 200
        })
        eq_(output['errno'], 0)

    def test_request_summary_method(self):
        output, req, res = self._request_summary(request_args={
            'method': DUMMY
        })
        eq_(output['method'], DUMMY)

    def test_request_summary_path(self):
        output, req, res = self._request_summary(request_args={
            'path': DUMMY
        })
        eq_(output['path'], DUMMY)

    def test_request_summary_t(self):
        output, req, res = self._request_summary()
        eq_(output['t'], req.finish_time - req.start_time)

    def test_request_summary_predicates_ok(self):
        ok_(not any(self._predicates('the mart').values()))

    def test_request_summary_query_too_long(self):
        ok_(self._predicates('q' * 25)['query_length'])

    def test_request_summary_query_is_protocol(self):
        ok_(self._predicates('http://')['is_protocol'])
        ok_(self._predicates('https://')['is_protocol'])
        ok_(self._predicates('file://')['is_protocol'])
        ok_(not self._predicates('hello: //')['is_protocol'])
        ok_(not self._predicates('hello ://')['is_protocol'])

    def test_request_summary_query_is_hostname(self):
        ok_(self._predicates('www.m')['is_hostname'])
        ok_(self._predicates('thisislong.but')['is_hostname'])
        ok_(not self._predicates('hello. friend')['is_hostname'])

    def test_request_summary_query(self):
        eq_(self._query(DUMMY)[0]['query'], DUMMY)

    def test_request_summary_status_code_200(self):
        output, req, res = self._request_summary(response_args={
            'status_code': 200
        })
        eq_(output['status_code'], 200)

    def test_request_summary_status_code_400(self):
        output, req, res = self._request_summary(response_args={
            'status_code': 400
        })
        eq_(output['status_code'], 400)

    def test_request_summary_classifiers(self):
        output, req, res = self._request_summary(response_args={
            'data': WITH_CLASSIFIERS
        })
        eq_(set(output['classifiers']),
            set(list(WITH_CLASSIFIERS['enhancements'].keys())))
