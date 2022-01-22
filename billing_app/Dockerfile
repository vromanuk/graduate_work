FROM python:3.9-slim-buster

RUN apt update && apt upgrade -y && apt install -y netcat

WORKDIR /app

ADD requirements requirements
RUN pip3 install --upgrade pip && pip3 install -r requirements/production.txt

ADD . docker-entrypoint.sh ./

WORKDIR /app

ENTRYPOINT ["/app/docker-entrypoint.sh"]