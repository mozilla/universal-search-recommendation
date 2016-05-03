from unittest import TestCase

from recommendation.search.classification.base import BaseClassifier


BEST_RESULT = {
    'url': ''
}
ALL_RESULTS = [BEST_RESULT]


class TestBaseClassifier(TestCase):
    def setUp(self):
        self.instance = BaseClassifier(BEST_RESULT, ALL_RESULTS)

    def test_is_match(self):
        with self.assertRaises(NotImplementedError):
            self.instance.is_match(self.instance.best_result,
                                   self.instance.all_results)

    def test_enhance(self):
        with self.assertRaises(NotImplementedError):
            self.instance.enhance()
