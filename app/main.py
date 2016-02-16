import hashlib

from flask import abort, Flask, jsonify, request

from app import conf
from app.cors import cors_headers
from app.util import make_queue
from app.memcached import memcached
from app.search.recommendation import SearchRecommendation


application = Flask(__name__)
application.after_request(cors_headers)
application.config.update(
    CELERY_BROKER_URL=conf.CELERY_BROKER_URL,
    DEBUG=conf.DEBUG
)
queue = make_queue(application)


@queue.task(name='main.recommend')
def recommend(q, key):
    recommendation = SearchRecommendation(q).do_search(q)
    memcached.set(key, recommendation)
    return recommendation


@application.route('/')
def main():
    q = request.args.get('q')
    if not q:
        abort(400)
    key = '_'.join([
        conf.KEY_PREFIX,
        hashlib.md5(str(q).encode('utf-8')).hexdigest()
    ])
    try:
        response = memcached.get(key)
    except Exception as e:
        if application.config['DEBUG']:
            return jsonify({e.__class__.__name__: e.args}), 500
        return jsonify({}), 500
    if not response:
        recommend.delay(q, key)
        return jsonify({}), 202
    else:
        return jsonify(response), 200
