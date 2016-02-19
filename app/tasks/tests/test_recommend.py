from unittest import TestCase

from mock import patch
from nose.tools import eq_

from app.tests.memcached import mock_memcached


KEY = 'query_key'
QUERY = 'frend'
RESULTS = {
    'hello': 'frend'
}


@patch('app.tasks.task_recommend.memcached', mock_memcached)
class TestRecommendTask(TestCase):

    @patch('app.search.recommendation.SearchRecommendation.do_search')
    def test_recommend(self, mock_do_search):
        from app.tasks.task_recommend import recommend
        mock_do_search.return_value = RESULTS
        results = recommend.apply(args=[QUERY, KEY]).get()
        eq_(results, RESULTS)
        eq_(mock_memcached.get(KEY), RESULTS)
