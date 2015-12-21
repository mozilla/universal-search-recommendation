import os
import sys

from flask import abort, Flask, jsonify, request

from search.recommendation import SearchRecommendation

import conf
from memorize import CacheMissError


sys.path.append(os.path.dirname(__file__))
app = Flask(__name__)

@app.route('/')
def main():
    q = request.args.get('q')
    if not q:
        abort(400)
    try:
        search = SearchRecommendation(q, request)
    except CacheMissError:
        return jsonify({}), 202
    else:
        return jsonify(search.recommendation), 200


if __name__ == '__main__':
    print('Running server on http://%s:%d' % (conf.HOST, conf.PORT))
    app.run(debug=conf.DEBUG, host=conf.HOST, port=conf.PORT)
