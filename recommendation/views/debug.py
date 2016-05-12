from flask import Blueprint, render_template, request

from recommendation.search.recommendation import SearchRecommendation


debug = Blueprint('debug', __name__)


@debug.route('/debug')
def view():
    query = request.args.get('q')
    recommendation = SearchRecommendation(query, debug=True) if query else None
    if recommendation:
        recommendation.do_search(query)
    return render_template('debug.html', recommendation=recommendation), 200
