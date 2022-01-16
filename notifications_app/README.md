[![CI](https://github.com/vromanuk/notifications_sprint_1/actions/workflows/ci.yml/badge.svg)](https://github.com/vromanuk/notifications_sprint_1/actions/workflows/ci.yml)
# Notifications API service

Сервис отвечает за создание отложенных задач через Django-админку, а также за отправку различных нотификаций.

## How to run

Для локального запуска, воспользуйтесь следующей командой:
`docker-compose -f local.yml up --build -d`

После этого, необходимо создать суперпользователя (для того, чтобы запустить скрипт локально, нужно установить `POSTGRES_HOST=localhost`):

`python manage.py create_default_superuser`

Далее, для email рассылок, перейдите на этот адрес:
`localhost:8000/admin`
