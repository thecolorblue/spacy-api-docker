FROM debian:sid
MAINTAINER Brad Davis <brad.bdavis1@gmail.com>

ENV LANG en
ENV PORT 5000

RUN apt-get update
RUN apt-get install -y python3 build-essential gcc g++ python3-dev python3-setuptools python3-pip
RUN export PIP_CERT=`python3 -m pip._vendor.requests.certs`

COPY requirements.txt /usr/spacyapi/requirements.txt
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r /usr/spacyapi/requirements.txt

RUN python3 -m spacy.${LANG}.download parser

RUN mkdir -p /usr/spacyapi
COPY . /usr/spacyapi/

ENTRYPOINT cd /usr/spacyapi && python3 server.py

EXPOSE ${PORT}
