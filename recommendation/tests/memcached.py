class FakeMemcached(object):
    """
    Fake Memcached client that can be used to simulate basic get/set/flush_all
    operations of pylibmc with no true persistance. It can be used to mock the
    `memorize` decorator like so:

    from unittest.mock import patch
    from recommendation.tests.memcached import mock_memcached

    def tearDown(self):
        mock_memcached.flush_all()

    @patch('recommendation.memorize.memcached', mock_memcached)
    def test_foo(self):
        assert(True)
    """
    def __init__(self):
        self.storage = {}

    def flush_all(self):
        self.storage = {}

    def set(self, key, value, time=None):
        self.storage[key] = value

    def get(self, key):
        return self.storage.get(key, None)

mock_memcached = FakeMemcached()
