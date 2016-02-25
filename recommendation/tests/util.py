from flask.ext.testing import TestCase as FlaskTestCase

from recommendation.factory import create_app


class AppTestCase(FlaskTestCase):
    def create_app(self):
        app = create_app()
        app.config['DEBUG'] = self.debug
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        return app
