from nose.tools import eq_, ok_

from app.tests.util import AppTestCase


class TestCreateQueue(AppTestCase):
    def test_lbheartbeat(self):
        response = self.client.get('/lbheartbeat')
        eq_(response.status_code, 200)
        ok_(not response.data)
