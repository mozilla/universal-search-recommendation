from flask import abort, Flask, jsonify, request

from app.conf import DEBUG
from app.memorize import CacheMissError
from app.search.recommendation import SearchRecommendation


app = Flask(__name__)
app.config['DEBUG'] = DEBUG


@app.route('/')
def main():
    q = request.args.get('q')
    if not q:
        abort(400)
    try:
        search = SearchRecommendation(q, request)
    except CacheMissError:
        return jsonify({}), 202
    except Exception as e:
        if app.config['DEBUG']:
            return jsonify({e.__class__.__name__: e.args}), 500
        return jsonify({}), 500
    else:
        return jsonify(search.recommendation), 200
