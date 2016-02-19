from flask import Blueprint


status = Blueprint('status', __name__)


@status.route('/lbheartbeat')
def lbheartbeat():
    return ('', 200)
