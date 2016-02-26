from recommendation import tasks  # noqa
from recommendation.factory import create_app, create_queue

application = create_app()
celery = create_queue()
