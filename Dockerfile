FROM ubuntu:12.04
MAINTAINER Siclic

# Set some ENV variables
ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://archive.ubuntu.com/ubuntu precise main universe" > /etc/apt/sources.list
RUN apt-get update
RUN apt-get -y install python-yaml

# Create PushService application dir
RUN mkdir -p /srv/pushservice/logs
RUN mkdir -p /srv/pushservice/run
RUN mkdir -p /srv/pushservice/config
RUN mkdir /data
RUN mkdir /ciril

ADD config/config-docker.yml /srv/pushservice/config/config.yml
ADD config/logging_config.yml /srv/pushservice/config/logging_config.yml
ADD push_service.py /srv/pushservice/push_service.py

EXPOSE 44001

WORKDIR /srv/pushservice

CMD python push_service.py
