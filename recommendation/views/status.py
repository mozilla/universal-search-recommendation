from os import path

import kombu
import redis
from celery.app.control import Control
from flask import Blueprint, jsonify, send_file

from recommendation import conf
from recommendation.memcached import memcached
from recommendation.views.static import STATIC_DIR


status = Blueprint('status', __name__)


@status.route('/__version__')
def version():
    return send_file(path.join(STATIC_DIR, 'version.json'))


@status.route('/__lbheartbeat__')
def lbheartbeat():
    return ('', 200)


class ServiceDown(RuntimeError):
    pass


def memcached_status():
    """
    Raises ServiceDown if the memcached server is down. `memcached.set` returns
    `True` if the operation was performed correctly, and `0` if not.
    """
    if not memcached.set('ping', 'pong'):
        raise ServiceDown()


def redis_status():
    """
    Raises ServiceDown if the Redis server used as a celery broker is down.
    """
    cxn = kombu.Connection(conf.CELERY_BROKER_URL)
    try:
        cxn.connect()
    except redis.exceptions.ConnectionError:
        raise ServiceDown()
    else:
        cxn.close()


def celery_status():
    """
    Raises ServiceDown if there are no Celery workers available.
    """
    from recommendation.factory import create_queue
    control = Control(app=create_queue())
    try:
        if not control.ping():
            raise ServiceDown()

    # Redis connection errors will be handled by `redis_status`.
    except redis.exceptions.ConnectionError:
        pass


@status.route('/__heartbeat__')
def heartbeat():
    """
    Sequentially runs each of the memcached, redis, and celery health checks.
    Returns a 500 if any raise ServiceDown, otherwise returns a 200 with an
    empty body.
    """
    celery, memcached, redis = True, True, True
    try:
        celery_status()
    except ServiceDown:
        celery = False
    try:
        memcached_status()
    except ServiceDown:
        memcached = False
    try:
        redis_status()
    except ServiceDown:
        redis = False
    return jsonify({
        'celery': celery,
        'memcached': memcached,
        'redis': redis
    }), (200 if all([celery, memcached, redis]) else 500)
