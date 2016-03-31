from recommendation.search.classification.embedly import (FaviconClassifier,
                                                          KeyImageClassifier)
from recommendation.search.classification.logo import LogoClassifier
from recommendation.search.classification.wikipedia import WikipediaClassifier


CLASSIFIERS = [
    FaviconClassifier,
    KeyImageClassifier,
    LogoClassifier,
    WikipediaClassifier,
]
