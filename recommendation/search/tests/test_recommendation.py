from unittest.mock import patch

from nose.tools import eq_, ok_

from recommendation.search.classification.embedly import FaviconClassifier
from recommendation.search.classification.tests.test_tld import DOMAIN
from recommendation.search.classification.tld import TLDClassifier
from recommendation.search.recommendation import SearchRecommendation
from recommendation.search.suggest.base import BaseSuggestionEngine
from recommendation.search.suggest.bing import BingSuggestionEngine
from recommendation.search.suggest.tests.test_bing import (
    QUERY as BING_QUERY, RESULTS as BING_RESULTS)
from recommendation.search.query.base import BaseQueryEngine
from recommendation.search.query.yahoo import YahooQueryEngine
from recommendation.search.query.tests.test_yahoo import (
    QUERY as YAHOO_QUERY, MOCK_RESPONSE as YAHOO_RESPONSE)
from recommendation.tests.memcached import mock_memcached
from recommendation.tests.util import AppTestCase


QUERY = 'Cubs'
RESULT = {
    'url': 'http://%s/' % DOMAIN
}
SUGGESTIONS = ['a', 'b', 'c']


class TestSearchRecommendation(AppTestCase):
    def setUp(self):
        self.instance = SearchRecommendation('')

    def tearDown(self):
        mock_memcached.flush_all()

    def test_get_suggestion_engine(self):
        engine = self.instance.get_suggestion_engine()
        ok_(issubclass(engine, BaseSuggestionEngine))

    def test_get_query_engine(self):
        engine = self.instance.get_query_engine()
        ok_(issubclass(engine, BaseQueryEngine))

    @patch('recommendation.search.classification.tld.TLDClassifier'
           '.is_match')
    def test_get_classifiers(self, mock_match):
        mock_match.return_value = True
        classifiers = self.instance.get_classifiers(RESULT, [RESULT])
        eq_(len(classifiers), 2)

        classifier_classes = [FaviconClassifier, TLDClassifier]
        for index, classifier in enumerate(classifiers):
            ok_(isinstance(classifier, classifier_classes[index]))
        return classifiers

    @patch('recommendation.search.recommendation.CLASSIFIERS', [TLDClassifier])
    @patch('recommendation.search.classification.tld.TLDClassifier'
           '.is_match')
    def test_all_classifiers(self, mock_match):
        mock_match.return_value = False
        instance = SearchRecommendation('', debug=True)
        all_classifiers = instance.all_classifiers(RESULT, [RESULT])
        eq_(len(all_classifiers), 1)
        eq_(all_classifiers[0]['name'], TLDClassifier.__name__)
        eq_(all_classifiers[0]['is_match'], False)
        eq_(all_classifiers[0]['result'], None)

    @patch(('recommendation.search.recommendation.SearchRecommendation'
            '.get_suggestion_engine'))
    @patch('recommendation.search.suggest.bing.BingSuggestionEngine.search')
    def test_get_suggestions(self, mock_bing, mock_suggestion_engine):
        mock_bing.return_value = BING_RESULTS
        mock_suggestion_engine.return_value = BingSuggestionEngine
        eq_(self.instance.get_suggestions(BING_QUERY), BING_RESULTS)
        eq_(mock_bing.call_count, 1)

    def test_get_top_suggestion(self):
        eq_(self.instance.get_top_suggestion(BING_RESULTS), BING_RESULTS[0])

    def test_get_top_suggestion_empty(self):
        self.instance.query = QUERY
        eq_(self.instance.get_top_suggestion([]), QUERY)

    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.get_query_engine')
    @patch('recommendation.search.query.yahoo.YahooQueryEngine.search')
    def test_do_query(self, mock_yahoo, mock_query_engine):
        response = YAHOO_RESPONSE['bossresponse']['web']['results'][0]
        mock_yahoo.return_value = response
        mock_query_engine.return_value = YahooQueryEngine
        eq_(self.instance.do_query(YAHOO_QUERY), response)
        eq_(mock_yahoo.call_count, 1)

    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.all_classifiers')
    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.get_classifiers')
    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.do_query')
    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.get_top_suggestion')
    @patch('recommendation.search.recommendation.SearchRecommendation'
           '.get_suggestions')
    @patch('recommendation.memorize.memcached', mock_memcached)
    def test_do_search_get_recommendation(self, mock_suggestions,
                                          mock_top_suggestion, mock_result,
                                          mock_classifiers,
                                          mock_all_classifiers):
        suggestions = BING_RESULTS
        top_suggestion = BING_RESULTS[0]
        result = YAHOO_RESPONSE['bossresponse']['web']['results'][0]
        classifiers = [TLDClassifier(result, [result])]

        mock_suggestions.return_value = suggestions
        mock_top_suggestion.return_value = top_suggestion
        mock_result.return_value = result, [result]
        mock_classifiers.return_value = classifiers

        search = self.instance.do_search(QUERY)

        ok_(all([k in search for k in ['enhancements', 'query', 'result']]))
        eq_(list(search['enhancements'].keys()), [c.type for c in classifiers])
        eq_(search['enhancements']['tld'], classifiers[0].enhance())
        eq_(search['query']['completed'], top_suggestion)
        eq_(search['query']['original'], QUERY)
        eq_(search['result'], result)
        eq_(mock_all_classifiers.call_count, 0)

        SearchRecommendation('', debug=True).do_search('')
        eq_(mock_all_classifiers.call_count, 1)
