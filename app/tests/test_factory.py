from unittest import TestCase

from celery.app.base import Celery
from mock import patch
from nose.tools import eq_, ok_

from app.cors import cors_headers
from app.factory import create_app, create_queue
from app.tests.util import AppTestCase


BROKER_URL = 'http://celery.carrots/broccoli'


class TestCreateApp(TestCase):
    @patch('app.factory.conf.CELERY_BROKER_URL', BROKER_URL)
    def test_create_app(self):
        app = create_app()
        ok_(cors_headers in app.after_request_funcs[None])
        ok_(all(name in app.blueprints for name in ['main', 'status']))
        eq_(app.config['CELERY_BROKER_URL'], BROKER_URL)


class TestCreateQueue(AppTestCase):
    TEST_KEY = 'hello'
    TEST_VALUE = 'bar'

    def test_existing_app(self):
        self.app.config.update({self.TEST_KEY: self.TEST_VALUE})
        queue = create_queue(self.app)
        eq_(type(queue), Celery)
        eq_(queue.conf[self.TEST_KEY], self.TEST_VALUE)

    def test_new_app(self):
        self.app.config.update({self.TEST_KEY: self.TEST_VALUE})
        queue = create_queue()
        eq_(type(queue), Celery)
        ok_(self.TEST_KEY not in queue.conf.keys())
