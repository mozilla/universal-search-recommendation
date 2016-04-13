from logging import INFO, StreamHandler
from sys import stdout

from celery import Celery
from flask import Flask

from recommendation import celeryconfig
from recommendation import conf
from recommendation.cors import cors_headers
from recommendation.mozlog.formatter import MozLogFormatter
from recommendation.mozlog.middleware import request_timer, request_summary
from recommendation.views.dummy import dummy
from recommendation.views.main import main
from recommendation.views.static import static
from recommendation.views.status import status


def create_app():
    app = Flask(__name__)

    # Append CORS headers to each request.
    app.after_request(cors_headers)

    # Register views.
    app.register_blueprint(main)
    app.register_blueprint(static)
    app.register_blueprint(status)

    # Use a dummy data generator while Yahoo BOSS access is being sorted out.
    app.register_blueprint(dummy)

    # Log using the mozlog format to stdout.
    handler = StreamHandler(stream=stdout)
    handler.setFormatter(MozLogFormatter(logger_name='universalSearch'))
    handler.setLevel(INFO)
    app.logger_name = 'request.summary'
    app.logger.addHandler(handler)
    app.logger.setLevel(INFO)

    # Use logging middleware.
    app.before_request(request_timer)
    app.after_request(request_summary)

    app.config.update(
        CELERY_BROKER_URL=conf.CELERY_BROKER_URL,
        DEBUG=conf.DEBUG
    )
    return app


def create_queue(app=None):
    app = app or create_app()

    queue = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    queue.conf.update(app.config)
    queue.config_from_object(celeryconfig)
    TaskBase = queue.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    queue.Task = ContextTask
    return queue
