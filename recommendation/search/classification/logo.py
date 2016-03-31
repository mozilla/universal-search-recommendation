import requests

from recommendation.search.classification.base import BaseClassifier


class LogoClassifier(BaseClassifier):
    """
    Classifier that is applied if the returned result is the root address of a
    domain name. Returns a URL to the logo or None.
    """
    type = 'logo'

    def _get_logo(self):
        return 'https://logo.clearbit.com/%s' % self.url.netloc

    def _logo_exists(self, url):
        response = requests.get(url)
        return response.status_code < 400

    def is_match(self, result):
        return self.url.path in ['/', '']

    def enhance(self):
        logo = self._get_logo()
        if not self._logo_exists(logo):
            return None
        return logo
