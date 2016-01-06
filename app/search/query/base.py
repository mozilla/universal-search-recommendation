import bleach

from app.memorize import memorize


class BaseQueryEngine(object):
    """
    Query engines are subclasses of this that are used to fetch the top search
    result for a search string.

    Example: "the martian" =>

    {
        "abstract": "The <b>Martian</b> is a 2011 science fiction novel...",
        "clickurl": "https://en.wikipedia.org/wiki/The_Martian_(Andy_Weir)",
        "date": "",
        "dispurl": "https://en.<b>wiki</b>pedia.org/<b>wiki/The_Martian...",
        "title": "The <b>Martian</b> (Weir novel) - Wikipedia, the free...",
        "url": "https://en.wikipedia.org/wiki/The_Martian_(Andy_Weir)"
    }
    """
    def __init__(self, query):
        self.query = query
        self.results = self.search(query)

    def fetch(self, query):
        """
        Passed a search string fragment, performs a search against an external
        API and returns the JSON results.
        """
        raise NotImplementedError()

    def sanitize_response(self, results):
        """
        Passed a JSON response from this query engine's API, sanitizes and
        normalizes those results, returning a list of them.
        """
        return results

    def get_best_result(self, results):
        """
        Passed a list of results, determines and returns the one that should be
        shown to the user.
        """
        return results[0]

    def sanitize_result(self, result):
        """
        Passed a result, sanitizes and normalizes it to return to the user.

        Currently produces:
        {
            'abstract': '',
            'title': '',
            'url': ''
        }

        Normalized values should be calculated in separate methods to provide
        subclasses easy hooks to override default values.
        """
        return {
            'abstract': self.get_result_abstract(result),
            'title': self.get_result_title(result),
            'url': self.get_result_url(result),
        }

    def _strip_html(self, string):
        """
        Strips HTML from the passed string.
        """
        return bleach.clean(string, tags=[], strip=True)

    def get_result_title(self, result):
        """
        Passed a result object, returns its title.
        """
        return self._strip_html(result['title'])

    def get_result_url(self, result):
        """
        Passed a result object, returns its url.
        """
        return result['url']

    def get_result_abstract(self, result):
        """
        Passed a result object, returns its abstract.
        """
        return self._strip_html(result['abstract'])

    @memorize(prefix='query', error_on_miss=True)
    def search(self, query):
        """
        Simple method wrapping the full search and processing lifecycle.
        Extracted from __init__ to allow it to be easily memoized.

        This should not need to be subclassed.
        """
        results = self.fetch(query)
        sanitized_results = self.sanitize_response(results)
        best_result = self.get_best_result(sanitized_results)
        return self.sanitize_result(best_result)
