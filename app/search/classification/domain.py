from app.search.classification.base import BaseClassifier


class DomainClassifier(BaseClassifier):
    """
    Classifier that is applied if the returned result is the root address of a
    domain name. Adds:

    fqdn - the fully qualified domain name
    logo - the URL to a logo, as determined by Clearbit.
    """
    type = 'domain'

    def is_match(self, result):
        return self.url.path in ['/', '']

    def enhance(self):
        return {
            'fqdn': self.url.netloc,
            'logo': 'https://logo.clearbit.com/%s' % self.url.netloc
        }
