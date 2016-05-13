from recommendation.search.classification.embedly import (FaviconClassifier,
                                                          WikipediaClassifier)
from recommendation.search.classification.movies import MovieClassifier
from recommendation.search.classification.tld import TLDClassifier


CLASSIFIERS = [
    FaviconClassifier,
    MovieClassifier,
    TLDClassifier,
    WikipediaClassifier
]
