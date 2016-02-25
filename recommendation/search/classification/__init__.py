from recommendation.search.classification.domain import DomainClassifier
from recommendation.search.classification.embedly import EmbedlyClassifier
from recommendation.search.classification.wikipedia import WikipediaClassifier


CLASSIFIERS = [
    DomainClassifier,
    EmbedlyClassifier,
    WikipediaClassifier,
]
