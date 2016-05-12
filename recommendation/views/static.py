from os import path, pardir
from flask import Blueprint, send_file


static = Blueprint('static', __name__)
STATIC_DIR = path.join(path.dirname(path.abspath(__file__)), pardir, 'static')


@static.route('/contribute.json')
def lbheartbeat():
    return send_file(path.join(STATIC_DIR, 'contribute.json'))


@static.route('/json-formatter.js')
def json_formatter():
    return send_file(path.join(STATIC_DIR, 'json-formatter.js'))
