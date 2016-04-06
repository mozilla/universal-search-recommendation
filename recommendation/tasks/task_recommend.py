from recommendation.conf import MEMCACHED_TTL
from recommendation.factory import create_queue
from recommendation.memcached import memcached
from recommendation.search.recommendation import SearchRecommendation


queue = create_queue()


@queue.task(name='main.recommend')
def recommend(q, key):
    recommendation = SearchRecommendation(q).do_search(q)
    memcached.set(key, recommendation, time=MEMCACHED_TTL)
    return recommendation
