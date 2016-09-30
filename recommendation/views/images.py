from urllib.parse import urlencode

import requests
from flask import abort, Blueprint, request, Response, stream_with_context

from recommendation import conf

EMBEDLY_RESIZE = 'https://i.embed.ly/1/display/resize'


images = Blueprint('images', __name__)


def make_embedly_url(url, **kwargs):
    """
    Passed the URL to an image, returns a string to the Embedly resize URL for
    that image. Accepts optional `width` and `height` keyword arguments.
    """
    qs = {}
    for param in ['width', 'height']:
        if param in kwargs:
            qs[param] = kwargs[param][0]
    qs['animate'] = 'false'
    qs['compresspng'] = 'true'
    qs['key'] = conf.EMBEDLY_API_KEY
    qs['url'] = url[0]
    return '{}?{}'.format(EMBEDLY_RESIZE, urlencode(qs))


@images.route('/images')
def proxy():
    try:
        url = make_embedly_url(**request.args)
    except (IndexError, TypeError):
        abort(400)
    try:
        req = requests.get(url, stream=True, timeout=10)
    except requests.RequestException:
        abort(400)
    if req.status_code != 200:
        abort(400)
    response = Response(stream_with_context(req.iter_content()),
                        content_type=req.headers['content-type'])
    response.headers['Cache-Control'] = 'max-age=%d' % conf.IMAGEPROXY_TTL
    return response
