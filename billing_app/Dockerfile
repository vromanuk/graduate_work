FROM python:3.9-slim-buster

RUN apt update && apt upgrade -y && apt install -y netcat

WORKDIR /app

ADD ./billing_app/requirements requirements
RUN pip3 install --upgrade pip && pip3 install -r requirements/production.txt

ADD ./billing_app ./billing_app/docker-entrypoint.sh ./

WORKDIR /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]