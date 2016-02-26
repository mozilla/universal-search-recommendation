from celery import Celery
from flask import Flask

from recommendation import conf
from recommendation.cors import cors_headers
from recommendation.views.main import main
from recommendation.views.static import static
from recommendation.views.status import status


def create_app():
    app = Flask(__name__)
    app.after_request(cors_headers)
    app.register_blueprint(main)
    app.register_blueprint(static)
    app.register_blueprint(status)
    app.config.update(
        CELERY_BROKER_URL=conf.CELERY_BROKER_URL,
        DEBUG=conf.DEBUG
    )
    return app


def create_queue(app=None):
    app = app or create_app()

    queue = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    queue.conf.update(app.config)
    TaskBase = queue.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    queue.Task = ContextTask
    return queue
