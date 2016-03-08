from urllib.parse import urlencode

from nose.tools import eq_, ok_

from recommendation.tests.util import AppTestCase


class TestDummyViews(AppTestCase):
    def _get(self, path):
        return self.client.get(path)

    def _query(self, query):
        url = '/dummy?%s' % urlencode({
            'q': query
        })
        return self._get(url)

    def test_no_query(self):
        eq_(self._get('/dummy').status_code, 400)

    def test_returns(self):
        response = self._query('hello')
        eq_(response.status_code, 200)
        ok_('enhancements' in response.json)
        ok_(all([k in response.json['enhancements'] for k in
                 ['embedly', 'domain']]))
        ok_('result' in response.json)
        ok_(all([k in response.json['result'] for k in
                 ['title', 'abstract', 'url']]))

    def test_idempotent(self):
        response_1 = self._query('frend')
        response_2 = self._query('frend')
        eq_(response_1.status_code, 200)
        eq_(response_2.status_code, 200)
        eq_(response_1.json, response_2.json)
