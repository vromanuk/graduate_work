FROM python:3.9

ARG workdir=/opt/app

ADD ./requirements.txt $workdir/
WORKDIR $workdir

RUN pip3 install -r requirements.txt
ADD . $workdir

RUN python manage.py migrate
