# universal-search-recommendation
#
# VERSION 0.1

FROM python:3.5
MAINTAINER https://mail.mozilla.org/listinfo/testpilot-dev

RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid 10001 --shell /usr/sbin/nologin app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade --no-cache-dir -r /app/requirements.txt

COPY . /app
ENV PYTHONPATH $PYTHONPATH:/app

USER app
ENTRYPOINT /app/conf/web.sh
