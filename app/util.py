def make_queue(app):
    from celery import Celery
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
