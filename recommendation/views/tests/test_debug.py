from urllib.parse import urlencode
from unittest.mock import patch

from nose.tools import eq_

from recommendation.tests.util import AppTestCase


QUERY = 'frend'


class TestDebug(AppTestCase):
    def _get(self, path):
        return self.client.get(path)

    def _query(self, query):
        url = '/debug?%s' % urlencode({
            'q': query
        })
        return self._get(url)

    @patch('recommendation.views.debug.SearchRecommendation')
    def test_debug_no_query(self, mock_search_rec):
        response = self._get('/debug')
        eq_(mock_search_rec.call_count, 0)
        eq_(response.status_code, 200)

    @patch('recommendation.views.debug.SearchRecommendation')
    @patch('recommendation.views.debug.SearchRecommendation.do_search')
    @patch('recommendation.views.debug.render_template')
    def test_debug_query(self, mock_render, mock_do_search, mock_search_rec):
        mock_render.return_value = ''
        response = self._query(QUERY)
        eq_(mock_search_rec.call_count, 1)
        eq_(response.status_code, 200)
