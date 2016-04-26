from unittest import TestCase
from unittest.mock import patch

from nose.tools import eq_

from prepopulate import alexa, explode, queue, wikipedia


ALEXA = ['a.b.c', 'b.c', 'ab.c']
WIKIPEDIA = ['abc', 'abd']


class TestPrepopulateScript(TestCase):
    def setUp(self):
        self.queue = []

    def test_explode(self):
        eq_(list(explode('abc')), ['a', 'ab', 'abc'])

    @patch('prepopulate.MAX_LENGTH', 2)
    def test_explode_over_max(self):
        eq_(list(explode('abc')), ['a', 'ab'])

    @patch('prepopulate.recommend.delay')
    def test_queue(self, mock_delay):
        with patch('prepopulate.QUEUE', self.queue):
            queue('abc')
        eq_(self.queue, ['a', 'ab', 'abc'])
        eq_(mock_delay.call_count, len(self.queue))

    @patch('prepopulate.recommend.delay')
    def test_queue_multiple(self, mock_delay):
        with patch('prepopulate.QUEUE', self.queue):
            queue('abc')
            queue('abd')
        eq_(self.queue, ['a', 'ab', 'abc', 'abd'])
        eq_(mock_delay.call_count, len(self.queue))

    @patch('prepopulate.recommend.delay')
    @patch('prepopulate.open')
    def test_wikipedia(self, mock_open, mock_delay):
        manager = mock_open.return_value.__enter__.return_value
        manager.readlines.return_value = WIKIPEDIA
        with patch('prepopulate.QUEUE', self.queue):
            wikipedia()
        eq_(self.queue, ['a', 'ab', 'abc', 'abd'])
        eq_(mock_delay.call_count, len(self.queue))

    @patch('prepopulate.recommend.delay')
    @patch('prepopulate.open')
    def test_alexa(self, mock_open, mock_delay):
        manager = mock_open.return_value.__enter__.return_value
        manager.readlines.return_value = ALEXA
        with patch('prepopulate.QUEUE', self.queue):
            alexa()
        eq_(self.queue, ['a', 'b', 'ab'])
        eq_(mock_delay.call_count, len(self.queue))
