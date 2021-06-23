FROM python:3.9.5-alpine
LABEL maintainer = "Squid Productions"

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN mkdir /app
WORKDIR /app
COPY ./src /app

RUN adduser -D user
USER user