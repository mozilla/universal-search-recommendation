from app import tasks  # noqa
from app.factory import create_app, create_queue

application = create_app()
celery = create_queue()
