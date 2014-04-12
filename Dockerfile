FROM ubuntu:12.04
MAINTAINER Siclic

RUN apt-get update

# Set some ENV variables
ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get -q -y install python-yaml

# Create PushService application dir
RUN mkdir -p /srv/pushservice/logs
RUN mkdir -p /srv/pushservice/run
RUN mkdir -p /srv/pushservice/config
RUN mkdir /data
RUN mkdir /ciril

VOLUME /ciril

ADD config/config-docker.yml /srv/pushservice/config/config.yml
ADD config/logging_config.yml /srv/pushservice/config/logging_config.yml
ADD push_service.py /srv/pushservice/push_service.py

EXPOSE 44001

WORKDIR /srv/pushservice

CMD python /srv/pushservice/push_service.py
