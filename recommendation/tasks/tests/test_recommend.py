from unittest import TestCase
from unittest.mock import patch

from nose.tools import eq_, ok_

from recommendation.tests.memcached import mock_memcached
from recommendation.tasks.task_recommend import make_key


KEY = 'query_key'
QUERY = 'frend'
RESULTS = {
    'hello': 'frend'
}


@patch('recommendation.tasks.task_recommend.memcached', mock_memcached)
class TestRecommendTask(TestCase):

    @patch('recommendation.tasks.task_recommend.conf.KEY_PREFIX', KEY)
    def test_make_key(self):
        ok_(make_key(QUERY).startswith(KEY))
        eq_(make_key(QUERY), make_key(QUERY))

    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.do_search')
    @patch('recommendation.tasks.task_recommend.make_key')
    def test_recommend(self, mock_make_key, mock_do_search):
        from recommendation.tasks.task_recommend import recommend
        mock_make_key.return_value = KEY
        mock_do_search.return_value = RESULTS
        results = recommend.apply(args=[QUERY]).get()
        eq_(results, RESULTS)
        eq_(mock_memcached.get(KEY), RESULTS)
