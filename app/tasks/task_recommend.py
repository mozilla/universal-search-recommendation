from app.factory import create_queue
from app.memcached import memcached
from app.search.recommendation import SearchRecommendation


queue = create_queue()


@queue.task(name='main.recommend')
def recommend(q, key):
    recommendation = SearchRecommendation(q).do_search(q)
    memcached.set(key, recommendation)
    return recommendation
