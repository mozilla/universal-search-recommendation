from celery.app.control import Control
from flask import abort, Blueprint
from redis.exceptions import ConnectionError as RedisConnectionError

from app.memcached import memcached


status = Blueprint('status', __name__)


@status.route('/lbheartbeat')
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
    Since our application should not have access to the Redis server, we test
    this by instantiating a Celery Control and attempting to ping it.
    """
    from app.factory import create_queue
    try:
        Control(app=create_queue()).ping(timeout=1)
    except RedisConnectionError:
        raise ServiceDown()


def celery_status():
    """
    Raises ServiceDown if any Celery worker servers are down, if any clusters
    have no workers, or if any workers are down.
    """
    from app.factory import create_queue
    clusters = Control(app=create_queue()).ping(timeout=1)
    if not clusters:
        raise ServiceDown()
    for cluster in clusters:
        if not cluster:
            raise ServiceDown()
        for host, status in cluster.items():
            if 'ok' not in status or status['ok'] != 'pong':
                raise ServiceDown()


@status.route('/heartbeat')
def heartbeat():
    """
    Sequentially runs each of the memcached, redis, and celery health checks.
    Returns a 500 if any raise ServiceDown, otherwise returns a 200 with an
    empty body.
    """
    try:
        memcached_status()
        redis_status()
        celery_status()
    except ServiceDown:
        abort(500)
    return ('', 200)
