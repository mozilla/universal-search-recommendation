from recommendation.celery import celery  # noqa
from recommendation.factory import create_app

application = create_app()
