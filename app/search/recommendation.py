from app.memorize import memorize
from app.search.classification import CLASSIFIERS
from app.search.query.yahoo import YahooQueryEngine
from app.search.suggest.bing import BingSuggestionEngine


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
    def __init__(self, query, request):
        self.request = request
        self.recommendation = self.do_search(query)

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

    def get_classifiers(self, result):
        """
        Returns a list of instances for all applicable classifiers for the
        search.
        """
        return [i for i in [C(result) for C in CLASSIFIERS] if i.matches]

    def get_suggestions(self, query):
        """
        Queries the appropriate suggestion engine, returns the results.
        """
        return self.get_suggestion_engine()(query).results

    def get_top_suggestion(self, suggestions):
        """
        Passed the full list of search suggestion results, returns the
        suggestion to be used.
        """
        return suggestions[0]

    def do_query(self, query):
        """
        Queries the appropriate search engine, returns the top result.
        """
        return self.get_query_engine()(query).results

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

    @memorize(prefix='search')
    def do_search(self, query):
        """
        The full search lifecycle, encapsulated in a method for easy
        memoization.
        """
        self.query = query
        self.suggestions = self.get_suggestions(query)
        self.top_suggestion = self.get_top_suggestion(self.suggestions)
        self.result = self.do_query(self.top_suggestion)
        self.classifiers = self.get_classifiers(self.result)
        return self.get_recommendation(
            self.query, self.top_suggestion, self.classifiers, self.result)
