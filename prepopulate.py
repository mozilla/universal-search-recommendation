#!/usr/bin/env python

import re
from os import path
from sys import stdout

from recommendation.tasks.task_recommend import recommend


CWD = path.dirname(path.realpath(__file__))
MAX_LENGTH = 10
QUEUE = []


def explode(string):
    """
    Returns an iterator that yields every possible substring of that string,
    starting with length 1 and ending with length MAX_LENGTH.

    Example:
    >>> list(explode('Firefox'))
    ['F', 'Fi', 'Fir', 'Fire', 'Firef', 'Firefo', 'Firefox']
    >>> list(explode('Mozilla Firefox'))
    ['M', 'Mo', 'Moz', 'Mozi', 'Mozil', 'Mozill', 'Mozilla', 'Mozilla ',
     'Mozilla F', 'Mozilla Fi']
    """
    n = MAX_LENGTH if len(string) > MAX_LENGTH else len(string)
    for i in range(n):
        yield string[:(i + 1)]


def queue(query):
    """
    Explodes a string, then queues a task to generate a recommendation for each
    item yielded by that string unless this script has already done so.
    """
    for q in explode(query):
        if q and q not in QUEUE:
            QUEUE.append(q)
            recommend.delay(q)


def wikipedia():
    """
    Opens the Wikipedia data file, which contains the names of the 250 most
    popular articles, and queues every unique string it contains.

    Source: https://en.wikipedia.org/wiki/User:West.andrew.g/Popular_pages
    Retrieved: 18/04/2016
    """
    with open(path.join(CWD, 'data', 'wikipedia.txt'), 'r') as f:
        for article in f.readlines():
            queue(article)


def alexa():
    """
    Opens the Alexa data file, which contains the 1000 top domain names on the
    internet, and queues every unique string it contains.

    Source: http://s3.amazonaws.com/alexa-static/top-1m.csv.zip
    Retrieved: 18/04/2016
    """
    with open(path.join(CWD, 'data', 'alexa.txt'), 'r') as f:
        for domain in f.readlines():
            base = re.match(r'([^\.]+)', domain)
            if base.groups():
                queue(base.group(0))


if __name__ == '__main__':
    wikipedia()
    alexa()
    stdout.write('{:d} items queued.\n'.format(len(QUEUE)))
