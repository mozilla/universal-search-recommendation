from unittest import TestCase

from flask.app import Flask
from nose.tools import eq_, ok_


class TestCeleryApp(TestCase):
    def test_wsgi_app(self):
        from recommendation import wsgi as wsgi_module
        ok_(hasattr(wsgi_module, 'application'))
        ok_(hasattr(wsgi_module, 'celery'))

    def test_wsgi_app_type(self):
        from recommendation.wsgi import application
        eq_(type(application), Flask)

    def test_wsgi_app_singleton(self):
        """
        Tests that multiple imports of the application singleton have the same
        memory ID (i.e. is the same object).
        """
        from recommendation.wsgi import application as app1
        from recommendation.wsgi import application as app2
        eq_(id(app1), id(app2))
