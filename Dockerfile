FROM python:3.9.6-alpine3.14 as base

COPY ./requirements.txt /app/requirements.txt

ENV ENV="PROD"

WORKDIR /app

RUN apk update && apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo

RUN pip install -r requirements.txt

COPY ./ /app

EXPOSE 8000

RUN chmod +x entrypoint.sh

ENTRYPOINT ./entrypoint.sh
