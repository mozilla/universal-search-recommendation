from urllib.parse import parse_qs, urlparse

from flask import current_app, url_for


def image_url(url, **kwargs):
    if not url:
        return
    kwargs['url'] = url
    parsed = urlparse(url)

    # If the image is already being proxied by Embedly, pull the `url`
    # querystring param out and use that instead to prevent double-billing.
    if parsed.netloc == 'i.embed.ly':
        qs = parse_qs(parsed.query)
        try:
            kwargs['url'] = qs['url'][0]
        except (IndexError, KeyError):
            pass

    with current_app.app_context():
        return url_for('images.proxy', **kwargs)
