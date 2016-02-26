import json
from os import path

from nose.tools import eq_

from recommendation.tests.util import AppTestCase
from recommendation.views.static import STATIC_DIR


class TestStaticViews(AppTestCase):
    def test_contribute(self):
        response = self.client.get('/contribute.json')
        eq_(response.status_code, 200)
        with open(path.join(STATIC_DIR, 'contribute.json')) as file_data:
            eq_(json.load(file_data), response.json)
