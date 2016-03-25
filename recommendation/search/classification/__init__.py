from recommendation.search.classification.domain import DomainClassifier
from recommendation.search.classification.embedly import (FaviconClassifier,
                                                          KeyImageClassifier)
from recommendation.search.classification.wikipedia import WikipediaClassifier


CLASSIFIERS = [
    DomainClassifier,
    FaviconClassifier,
    KeyImageClassifier,
    WikipediaClassifier,
]
