from nose.tools import ok_

from app.cors import cors_headers
from app.tests.util import AppTestCase


class TestCORS(AppTestCase):
    def test_cors(self):
        headers = [
            'Access-Control-Allow-Headers',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Origin',
        ]
        ok_(all([header not in dict(self.app.response_class().headers).keys()
                 for header in headers]))
        cors_response = cors_headers(self.app.response_class())
        ok_(all([header in dict(cors_response.headers).keys()
                 for header in headers]))
