import hashlib

from recommendation import conf
from recommendation.factory import create_queue
from recommendation.memcached import memcached
from recommendation.search.recommendation import SearchRecommendation


queue = create_queue()


def make_key(query):
    return '_'.join([
        conf.KEY_PREFIX,
        hashlib.md5(str(query).encode('utf-8')).hexdigest()
    ])


@queue.task(name='main.recommend')
def recommend(query):
    recommendation = SearchRecommendation(query).do_search(query)
    key = make_key(query)
    memcached.set(key, recommendation, time=conf.MEMCACHED_TTL)
    return recommendation
