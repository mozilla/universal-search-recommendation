import json
import re
import time

from flask import current_app, request


IS_PROTOCOL = r'^[^\s]+\:\S'
IS_HOSTNAME = r'^[^\s]+\.\S'
LOG_PATH_BLACKLIST = [
    '/favicon.ico',
    '/__heartbeat__',
    '/__lbheartbeat__',
    '/nginx_status',
    '/robots.txt'
]


def request_timer():
    """
    before_request middleware that attaches the processing start time to the
    request object, for later performance assessment.
    """
    request.start_time = time.time()


def request_summary(response):
    """
    after_request middleware that generates and logs a mozlog-formatted log
    about the request.

    Read more:

    https://github.com/mozilla/universal-search/blob/master/docs/metrics.md
    https://github.com/mozilla-services/Dockerflow/blob/master/docs/mozlog.md
    """
    request.finish_time = time.time()
    response.direct_passthrough = False

    if request.path in LOG_PATH_BLACKLIST:
        return response

    log = {}
    query = request.args.get('q')
    data = response.get_data(as_text=True)
    try:
        body = json.loads(data)
    except json.decoder.JSONDecodeError:
        body = {}

    log['agent'] = request.headers.get('User-Agent')
    log['errno'] = 0 if response.status_code < 400 else response.status_code
    log['lang'] = request.headers.get('Accept-Language')
    log['method'] = request.method
    log['path'] = request.path
    log['t'] = (request.finish_time - request.start_time) * 1000 # in ms

    if query:
        log['predicates.query_length'] = len(query) > 20
        log['predicates.is_protocol'] = (re.match(IS_PROTOCOL, query) is not
                                          None)
        log['predicates.is_hostname'] = (re.match(IS_HOSTNAME, query) is not
                                          None)

        if not any([log['predicates.query_length'],
                    log['predicates.is_protocol'],
                    log['predicates.is_hostname']]):
            log['query'] = query if query else None
            log['status_code'] = response.status_code
            classifiers = body.get('enhancements')
            log['classifiers'] = (list(classifiers.keys()) if classifiers else
                                  [])

    current_app.logger.info('', extra=log)

    return response
