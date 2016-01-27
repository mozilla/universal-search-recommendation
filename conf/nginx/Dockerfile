# universal-search-recommendation-proxy
#
# VERSION 0.1

FROM nginx:1.9.9
MAINTAINER https://mail.mozilla.org/listinfo/testpilot-dev

RUN rm /etc/nginx/conf.d/default.conf
COPY recommendation.conf /etc/nginx/conf.d/
