from nose.tools import eq_

from recommendation.tests.util import AppTestCase


class TestStaticViews(AppTestCase):
    files = [
        'contribute.json',
        'json-formatter.js'
    ]

    def test_files(self):
        for f in self.files:
            response = self.client.get('/{}'.format(f))
            eq_(response.status_code, 200)
