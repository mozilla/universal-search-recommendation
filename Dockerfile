# universal-search-recommendation
#
# VERSION 0.1

FROM python:3.5
MAINTAINER https://mail.mozilla.org/listinfo/testpilot-dev

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid 10001 --shell /usr/sbin/nologin app

# Install libmemcached-dev, whose C libraries are required by pylibmc.
RUN apt-get -qq update && apt-get -qq install -y libmemcached-dev=1.0.18-4

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade --no-cache-dir -r /app/requirements.txt

COPY . /app
ENV PYTHONPATH $PYTHONPATH:/app

USER app
EXPOSE 8000
ENTRYPOINT ["/app/conf/web.sh"]
