import pickle
from unittest import TestCase

from mock import patch
from nose.tools import eq_, ok_
from wrapt import ObjectProxy

from app.memorize import CacheMissError, memorize, MemorizedObject
from app.tests.memcached import mock_memcached


PREFIX = 'my_prefix'


class SampleObject(object):
    @memorize()
    def no_args(self, *args, **kwargs):
        return object()

    @memorize()
    def no_args_2(self, *args, **kwargs):
        return object()

    @memorize(prefix=PREFIX)
    def prefix(self, *args, **kwargs):
        return object()

    @memorize(error_on_miss=True)
    def error_on_miss(self, *args, **kwargs):
        return object()


class TestMemorizedObject(TestCase):
    def setUp(self):
        self.wrapped_object = [1, 2, 3]
        self.instance = MemorizedObject(self.wrapped_object)

    def test_reduce(self):
        pickle.dumps(self.wrapped_object)
        with self.assertRaises(pickle.PicklingError):
            UNPICKLEABLE = type('UNPICKLEABLE', (ObjectProxy,), {})
            pickle.dumps(MemorizedObject(UNPICKLEABLE(self.wrapped_object)))

    def test_repr(self):
        eq_(self.instance.__repr__(), self.instance.__wrapped__.__repr__())

    def test_from_cache(self):
        eq_(self.instance.from_cache, False)
        self.instance.from_cache = True
        eq_(self.instance.from_cache, True)
        self.instance.from_cache = False
        eq_(self.instance.from_cache, False)
        with self.assertRaises(RuntimeError):
            self.instance.from_cache = 'string'

    def test_cache_key(self):
        DUMMY_KEY = 'abc123'
        eq_(self.instance.cache_key, None)
        self.instance.cache_key = DUMMY_KEY
        eq_(self.instance.cache_key, DUMMY_KEY)
        with self.assertRaises(RuntimeError):
            self.instance.cache_key = True


@patch('app.memorize.memcached', mock_memcached)
class TestMemorize(TestCase):
    def setUp(self):
        self.obj = SampleObject()

    def tearDown(self):
        mock_memcached.flush_all()

    def _fn(self, fn, *args, **kwargs):
        return memorize()(fn)

    def _memorized(self, function_name, *args, **kwargs):
        if not function_name:
            function_name = 'no_args'
        fn = getattr(self.obj, function_name)
        return self._fn(fn)(*args, **kwargs)

    def _key(self, *args, **kwargs):
        fn = kwargs.pop('fn', None)
        return self._memorized(fn, *args, **kwargs).cache_key

    def test_cache_key_varies(self):
        eq_(self._key(), self._key())
        eq_(self._key(fn='prefix'), self._key(fn='prefix'))
        eq_(self._key('a'), self._key('a'))
        ok_(self._key('a') != self._key('b'))
        eq_(self._key(b='c'), self._key(b='c'))
        ok_(self._key(b='c') != self._key(b='d'))
        eq_(self._key('a', b='c'), self._key('a', b='c'))
        ok_(self._key('a', b='c') != self._key('b', b='c'))
        ok_(self._key('a', b='c') != self._key('a', b='d'))
        ok_(self._key() != self._key('a'))
        ok_(self._key('a') != self._key(b='c'))
        ok_(self._key(b='c') != self._key('a', b='c'))
        ok_(self._key(), self._key(fn='no_args_2'))
        ok_(self._key(), self._key(fn='prefix'))

    def test_error_on_miss(self):
        self._memorized('no_args')
        with self.assertRaises(CacheMissError):
            self._memorized('error_on_miss')

    def test_memorized_object_props(self):
        obj_cold = self._memorized('no_args')
        obj_warm = self._memorized('no_args')
        eq_(obj_cold, obj_warm)
        ok_(not obj_cold.from_cache)
        ok_(obj_warm.from_cache)
        eq_(obj_cold.cache_key, obj_warm.cache_key)
