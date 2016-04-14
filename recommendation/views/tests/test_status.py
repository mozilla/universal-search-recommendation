import json
from os import path

from mock import patch
from nose.tools import eq_, ok_
from redis.exceptions import ConnectionError as RedisError

from recommendation.views.static import STATIC_DIR
from recommendation.views.status import (celery_status, memcached_status,
                                         redis_status, ServiceDown)
from recommendation.tests.util import AppTestCase


MEMCACHED_WORKER_BAD = {'not ok': 'not pong'}
MEMCACHED_WORKER_OK = {'ok': 'pong'}

MEMCACHED_CLUSTER_BAD = {
    'host1': MEMCACHED_WORKER_OK,
    'host2': MEMCACHED_WORKER_BAD
}
MEMCACHED_CLUSTER_NO_WORKERS = {}
MEMCACHED_CLUSTER_OK = {
    'host1': MEMCACHED_WORKER_OK,
    'host2': MEMCACHED_WORKER_OK
}

MEMCACHED_PING_BAD = [MEMCACHED_CLUSTER_OK, MEMCACHED_CLUSTER_BAD]
MEMCACHED_PING_NO_CLUSTERS = []
MEMCACHED_PING_NO_WORKERS = [MEMCACHED_CLUSTER_OK,
                             MEMCACHED_CLUSTER_NO_WORKERS]
MEMCACHED_PING_OK = [MEMCACHED_CLUSTER_OK, MEMCACHED_CLUSTER_OK]


class TestStatusViews(AppTestCase):
    def test_version(self):
        response = self.client.get('/__version__')
        eq_(response.status_code, 200)
        with open(path.join(STATIC_DIR, 'version.json')) as file_data:
            eq_(json.load(file_data), response.json)

    def test_lbheartbeat(self):
        response = self.client.get('/__lbheartbeat__')
        eq_(response.status_code, 200)
        ok_(not response.data)

    @patch('recommendation.views.status.celery_status')
    @patch('recommendation.views.status.memcached_status')
    @patch('recommendation.views.status.redis_status')
    def test_heartbeat_pass(self, mock_celery, mock_memcached, mock_redis):
        response = self.client.get('/__heartbeat__')
        eq_(response.status_code, 200)
        eq_(mock_celery.call_count, 1)
        eq_(mock_memcached.call_count, 1)
        eq_(mock_redis.call_count, 1)
        ok_(response.json, {
            'celery': True,
            'memcached': True,
            'redis': True
        })

    @patch('recommendation.views.status.redis_status')
    @patch('recommendation.views.status.memcached_status')
    @patch('recommendation.views.status.celery_status')
    def test_heartbeat_celery(self, mock_celery, mock_memcached, mock_redis):
        mock_celery.side_effect = ServiceDown
        response = self.client.get('/__heartbeat__')
        eq_(response.status_code, 500)
        eq_(response.json['celery'], False)
        eq_(mock_celery.call_count, 1)

    @patch('recommendation.views.status.redis_status')
    @patch('recommendation.views.status.memcached_status')
    @patch('recommendation.views.status.celery_status')
    def test_heartbeat_memcached(self, mock_celery, mock_memcached,
                                 mock_redis):
        mock_memcached.side_effect = ServiceDown
        response = self.client.get('/__heartbeat__')
        eq_(response.status_code, 500)
        eq_(response.json['memcached'], False)
        eq_(mock_memcached.call_count, 1)

    @patch('recommendation.views.status.redis_status')
    @patch('recommendation.views.status.memcached_status')
    @patch('recommendation.views.status.celery_status')
    def test_heartbeat_redis(self, mock_celery, mock_memcached, mock_redis):
        mock_redis.side_effect = ServiceDown
        response = self.client.get('/__heartbeat__')
        eq_(response.status_code, 500)
        eq_(response.json['redis'], False)
        eq_(mock_redis.call_count, 1)

    @patch('recommendation.views.status.memcached.set')
    def test_memcached_status_pass(self, mock_set):
        mock_set.return_value = True
        memcached_status()
        self.assert_(True)

    @patch('recommendation.views.status.memcached.set')
    def test_memcached_status_fail(self, mock_set):
        mock_set.return_value = 0
        with self.assertRaises(ServiceDown):
            memcached_status()

    @patch('recommendation.views.status.Control.ping')
    def test_redis_status_pass(self, mock_ping):
        redis_status()
        self.assert_(True)

    @patch('recommendation.views.status.Control.ping')
    def test_redis_status_fail(self, mock_ping):
        mock_ping.side_effect = RedisError
        with self.assertRaises(ServiceDown):
            redis_status()

    @patch('recommendation.views.status.Control.ping')
    def test_celery_status_pass(self, mock_ping):
        mock_ping.return_value = MEMCACHED_PING_OK
        celery_status()
        self.assert_(True)

    @patch('recommendation.views.status.Control.ping')
    def test_celery_status_no_workers(self, mock_ping):
        mock_ping.return_value = MEMCACHED_PING_NO_WORKERS
        with self.assertRaises(ServiceDown):
            celery_status()

    @patch('recommendation.views.status.Control.ping')
    def test_celery_status_no_clusters(self, mock_ping):
        mock_ping.return_value = MEMCACHED_PING_NO_CLUSTERS
        with self.assertRaises(ServiceDown):
            celery_status()

    @patch('recommendation.views.status.Control.ping')
    def test_celery_status_workers_down(self, mock_ping):
        mock_ping.return_value = MEMCACHED_PING_BAD
        with self.assertRaises(ServiceDown):
            celery_status()
