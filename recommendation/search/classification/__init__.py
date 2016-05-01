from recommendation.search.classification.embedly import (FaviconClassifier,
                                                          WikipediaClassifier)
from recommendation.search.classification.tld import TLDClassifier


CLASSIFIERS = [
    FaviconClassifier,
    TLDClassifier,
    WikipediaClassifier
]
