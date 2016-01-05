from urllib.parse import urlparse


class BaseClassifier(object):
    """
    Classifiers are subclasses of this that can identify and enhance results
    based on characterstics of the result itself. It does this in two steps:

    1) Passed a search result, determine if the enhancements should be applied.
       This may be done by analyzing the URL, title, or query itself.
    2) Create, return, and add a `dict` of additional metadata to the result.

    Subclasses of `BaseClassifier` should implement both the `is_match` and
    `enhancement` methods.

    Each recommendation is passed through each classifier in the order
    specified in the `CLASSIFIERS` list in `app.search.classification`.
    Enhancements may depend on enhancements that have been previously applied.

    Example: `WikipediaClassifier` determines if a search result is a
    Wikipedia article. If so, it queries the Wikipedia API for additional
    metadata about the article.

    Original result:

    {
      "enhancements": {},
      "query": {
        "completed": "wiki the martian",
        "original": "wiki the marti"
      },
      "result": {
        "abstract": "The Martian is a 2011 science fiction novel. It was...",
        "title": "The Martian (Weir novel) - Wikipedia, the free encyclopedia",
        "url": "https://en.wikipedia.org/wiki/The_Martian_(Andy_Weir)"
      }
    }

    If it matched (according to `is_match`), WikipediaClassifier would update
    that result with:

    {
        "enhancements": {
            "wikipedia": {
                "abstract": "The Martian is a 2011 science fiction novel...",
                "slug": "The_Martian_(Andy_Weir)",
                "title": "The Martian (Weir novel)"
            }
        }
    }
    """
    type = None

    def __init__(self, result):
        self.result = result
        self.url = urlparse(result['url'])
        self.matches = self.is_match(result)

    def is_match(self, result):
        """
        Returns a boolean indicating whether or not the passed result should be
        enhanced by this class.
        """
        raise NotImplementedError()

    def enhance(self):
        """
        Returns a dictionary of metadata that the passed result should be
        enhanced with.
        """
        raise NotImplementedError()
