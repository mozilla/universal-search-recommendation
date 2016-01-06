from app.memorize import memorize


class BaseSuggestionEngine(object):
    """
    Suggestion engines are subclasses of this that attempt to complete a search
    that is in the process of being typed.

    Example: "wiki the mar" => "wikipedia the martian"
    """
    def __init__(self, query):
        self.query = query
        self.results = self.search(query)

    def fetch(self, query):
        """
        Passed a search string fragment, performs a search against an external
        search suggestion and returns the JSON results.
        """
        raise NotImplementedError()

    def sanitize(self, results):
        """
        Passed a JSON response from this query engine's API, sanitizes and
        normalizes those results, returning a list of them.
        """
        return results

    @memorize(prefix='suggestion')
    def search(self, query):
        return self.sanitize(self.fetch(query))
