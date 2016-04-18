from flask import (abort, after_this_request, current_app, Blueprint, jsonify,
                   request)

from recommendation import conf
from recommendation.memcached import memcached


main = Blueprint('main', __name__)


@main.route('/')
def view():

    @after_this_request
    def cache_control_headers(response):
        if response.status_code == 200:
            response.headers['Cache-Control'] = 'max-age=%d' % conf.CACHE_TTL
        else:
            response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        return response

    from recommendation.tasks.task_recommend import make_key, recommend
    query = request.args.get('q')
    if not query:
        abort(400)
    key = make_key(query)

    try:
        response = memcached.get(key)
    except Exception as e:
        if current_app.config.get('DEBUG'):
            return jsonify({e.__class__.__name__: e.args}), 500
        return jsonify({}), 500
    if not response:
        recommend.delay(query)
        return jsonify({}), 202
    else:
        return jsonify(response), 200
