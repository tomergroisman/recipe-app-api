FROM python:3.9.5-alpine
LABEL maintainer = "Squid Productions"

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .temp-build-deps \
      gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .temp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./src /app

RUN adduser -D user
USER user