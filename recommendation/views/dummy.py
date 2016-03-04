import random

from flask import abort, Blueprint, jsonify, request

from recommendation.views.data.dummy import EMBEDLIES, RESULTS


dummy = Blueprint('dummy', __name__)


@dummy.route('/dummy')
def dummy_main():
    query = request.args.get('q')
    if not query:
        abort(400)
    random.seed(query)
    return jsonify({
        'enhancements': {
            'embedly': random.choice(EMBEDLIES)
        },
        'query': {
            'completed': query,
            'original': query
        },
        'result': random.choice(RESULTS)
    }), 200
