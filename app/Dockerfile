# universal-search-recommendation-app
#
# VERSION 0.1

FROM python:3.5
MAINTAINER https://mail.mozilla.org/listinfo/testpilot-dev

RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid 1001 --shell /usr/sbin/nologin app

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . /app
ENV PYTHONPATH $PYTHONPATH:/

USER app
