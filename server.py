import os
import sys

from app import conf
from app.main import app


sys.path.append(os.path.dirname(__file__))

if __name__ == '__main__':
    print('Running server on http://%s:%d' % (conf.HOST, conf.PORT))
    app.run(debug=conf.DEBUG, host=conf.HOST, port=conf.PORT)
