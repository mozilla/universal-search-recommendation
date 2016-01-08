from unittest import TestCase
from urllib.parse import ParseResult

from nose.tools import eq_, ok_

from app.search.classification.domain import DomainClassifier


class TestDomainClassifier(TestCase):
    def _result(self, url):
        return {
            'url': url
        }

    def _classifier(self, url):
        return DomainClassifier(self._result(url))

    def _matches(self, url):
        return self._classifier(url).is_match(self._result(url))

    def _enhance(self, url):
        return self._classifier(url).enhance()

    def test_init(self):
        url = 'http://www.mozilla.com'
        instance = self._classifier(url)
        ok_(instance.result)
        eq_(instance.result['url'], url)
        ok_(isinstance(instance.url, ParseResult))
        ok_(isinstance(instance.is_match(instance.result), bool))
        ok_(isinstance(instance.enhance(), dict))

    def test_is_match(self):
        eq_(self._matches('http://www.mozilla.com'), True)
        eq_(self._matches('http://www.mozilla.com/'), True)
        eq_(self._matches('http://www.mozilla.com/en_US'), False)
        eq_(self._matches('http://www.mozilla.com/en_US/'), False)

    def test_enhance(self):
        enhancement = self._enhance('http://www.mozilla.com/en_US')
        eq_(enhancement['fqdn'], 'www.mozilla.com')
        eq_(enhancement['logo'], 'https://logo.clearbit.com/www.mozilla.com')
