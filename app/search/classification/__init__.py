from app.search.classification.domain import DomainClassifier
from app.search.classification.embedly import EmbedlyClassifier
from app.search.classification.wikipedia import WikipediaClassifier


CLASSIFIERS = [
    DomainClassifier,
    EmbedlyClassifier,
    WikipediaClassifier,
]
