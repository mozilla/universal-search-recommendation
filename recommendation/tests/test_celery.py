from unittest import TestCase

from celery.app.base import Celery
from nose.tools import eq_, ok_

from recommendation.celery import celery


class TestCeleryApp(TestCase):
    def test_celery_app(self):
        from recommendation import celery as celery_module
        ok_(hasattr(celery_module, 'celery'))

    def test_celery_app_type(self):
        eq_(type(celery), Celery)

    def test_celery_app_singleton(self):
        from recommendation.celery import celery as celery_2
        eq_(id(celery), id(celery_2))
