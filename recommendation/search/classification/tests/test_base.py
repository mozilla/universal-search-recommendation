from unittest import TestCase

from recommendation.search.classification.base import BaseClassifier


class TestBaseClassifier(TestCase):
    def setUp(self):
        self.instance = BaseClassifier({
            'url': ''
        })

    def test_is_match(self):
        with self.assertRaises(NotImplementedError):
            self.instance.is_match(self.instance.result)

    def test_enhance(self):
        with self.assertRaises(NotImplementedError):
            self.instance.enhance()
