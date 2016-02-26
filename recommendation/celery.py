from recommendation import tasks  # noqa
from recommendation.factory import create_queue

celery = create_queue()
