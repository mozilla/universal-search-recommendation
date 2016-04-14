from unittest import TestCase
from unittest.mock import patch
from urllib.parse import ParseResult

import responses
from nose.tools import eq_, ok_

from recommendation.search.classification.logo import LogoClassifier


DOMAIN = 'www.mozilla.com'
URL = 'http://%s/' % DOMAIN
LOGO = 'https://logo.clearbit.com/%s' % DOMAIN


class TestLogoClassifier(TestCase):
    def _result(self, url):
        return {
            'url': url
        }

    def _classifier(self, url):
        return LogoClassifier(self._result(url))

    def _matches(self, url):
        return self._classifier(url).is_match(self._result(url))

    def _enhance(self, url):
        return self._classifier(url).enhance()

    def test_get_logo(self):
        eq_(self._classifier(URL)._get_logo(), LOGO)

    @responses.activate
    def test_logo_exists_ok(self):
        responses.add(responses.GET, LOGO, status=200)
        eq_(self._classifier(URL)._logo_exists(LOGO), True)

    @responses.activate
    def test_logo_exists_invalid(self):
        responses.add(responses.GET, LOGO, status=400)
        eq_(self._classifier(URL)._logo_exists(LOGO), False)

    @responses.activate
    def test_logo_exists_missing(self):
        responses.add(responses.GET, LOGO, status=404)
        eq_(self._classifier(URL)._logo_exists(LOGO), False)

    @responses.activate
    def test_init(self):
        responses.add(responses.GET, LOGO, status=200)
        instance = self._classifier(URL)
        ok_(instance.result)
        eq_(instance.result['url'], URL)
        ok_(isinstance(instance.url, ParseResult))
        ok_(isinstance(instance.is_match(instance.result), bool))
        ok_(isinstance(instance.enhance(), str))

    def test_is_match(self):
        eq_(self._matches('http://%s' % DOMAIN), True)
        eq_(self._matches('http://%s/' % DOMAIN), True)
        eq_(self._matches('http://%s/en_US' % DOMAIN), False)
        eq_(self._matches('http://%s/en_US/' % DOMAIN), False)

    @patch(('recommendation.search.classification.logo.LogoClassifier.'
            '_logo_exists'))
    def test_enhance(self, mock_logo_exists):
        mock_logo_exists.return_value = False
        eq_(self._enhance(URL), None)
        mock_logo_exists.return_value = True
        eq_(self._enhance(URL), LOGO)
