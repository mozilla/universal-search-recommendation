from recommendation.search.classification import CLASSIFIERS
from recommendation.search.query.yahoo import YahooQueryEngine
from recommendation.search.suggest.bing import BingSuggestionEngine


class SearchRecommendation(object):
    """
    The master class that manages the full workflow from partial search
    string to recommendation. The current process involves the following steps:

    - Pass the partial search string to a suggestion engine. The suggestion
      engine class returns a completed search string.
    - Pass the completed search string to a query engine. That engine returns
      a completed search result, including a URL and title.
    - Pass the full search result through each classifier. Classifiers
      sequentially determine if they match the result, then enhance the result
      if so.
    """
    def __init__(self, query, debug=False):
        self.debug = debug
        self.query = query
        self.recommendation = None
        self.suggestion_engine = self.get_suggestion_engine()
        self.query_engine = self.get_query_engine()

    def get_suggestion_engine(self):
        """
        Determine and return the appropriate subclass of BaseSuggestionEngine
        to use to fetch search suggestions.
        """
        return BingSuggestionEngine

    def get_query_engine(self):
        """
        Determine and return the appropriate subclass of BaseQueryEngine to use
        to fetch results.
        """
        return YahooQueryEngine

    def all_classifiers(self, best_result, all_results):
        """
        Returns a list of all classifiers, regardless of applicability.
        """
        return [{
            'is_match': i.is_match(best_result, all_results),
            'name': i.__class__.__name__,
            'result': (i.enhance() if i.is_match(best_result, all_results)
                       else None)
        } for i in [C(best_result, all_results) for C in CLASSIFIERS]]

    def get_classifiers(self, best_result, all_results):
        """
        Returns a list of instances for all applicable classifiers for the
        search.
        """
        return [i for i in [C(best_result, all_results) for C in CLASSIFIERS]
                if i.is_match(best_result, all_results)]

    def get_suggestions(self, query):
        """
        Queries the appropriate suggestion engine, returns the results.
        """
        return list(self.suggestion_engine(query).search(query))

    def get_top_suggestion(self, suggestions):
        """
        Passed the full list of search suggestion results, returns the
        suggestion to be used.
        """
        try:
            return suggestions[0]
        except IndexError:
            return self.query

    def do_query(self, query):
        """
        Queries the appropriate search engine, returns a tuple containing both
        the top result and full result set.
        """
        return self.query_engine(query).search(query)

    def get_recommendation(self, query, suggestion, classifiers, result):
        """
        Constructs the full response from the query, suggestion, search result,
        and an array of each classifier.
        """
        return {
            'query': {
                'original': query,
                'completed': suggestion
            },
            'result': result,
            'enhancements': {c.type: c.enhance() for c in classifiers}
        }

    def do_search(self, query):
        """
        The full search lifecycle, encapsulated in a method for easy
        memoization.
        """
        self.query = query
        self.suggestions = self.get_suggestions(query)
        self.top_suggestion = self.get_top_suggestion(self.suggestions)
        self.best_result, self.all_results = self.do_query(self.top_suggestion)
        if self.debug:
            self.all_classifiers = self.all_classifiers(self.best_result,
                                                        self.all_results)
        self.classifiers = self.get_classifiers(self.best_result,
                                                self.all_results)
        self.recommendation = self.get_recommendation(
            self.query, self.top_suggestion, self.classifiers,
            self.best_result)
        return self.recommendation
