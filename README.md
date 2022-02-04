# Проектная работа: диплом

Сервис отвечает за создание подписки пользователя, обновление данные в авторизации, а также, отправке уведомлений после успешной оплаты подписки

## How to run

Для локального запуска, воспользуйтесь следующей командой:
`make docker-up`

Для проверки правильной работы сервиса, необходимо выполнить следующие команды:

- `curl http://localhost/auth/api/v1/smoke/` - проверка работы `auth_app`
- `curl http://localhost/api/v1/smoke/` - проверка работы `billing_app`
- `curl http://localhost/smoke/` - проверка работы `notifications_app`

Для остановки, воспользуйтесь командой:
`make docker-down`

Для прохождения стандартного флоу, воспользуйтесь следующими командами:
- Регистрация `curl --location --request POST 'http://localhost/auth/api/v1/register' \
--header 'Content-Type: application/json' \
--data-raw '{
    "login": "",
    "email": "",
    "password": ""
}'`
- Логин `curl --location --request POST 'http://localhost/auth/api/v1/login' \
--header 'Content-Type: application/json' \
--data-raw '{
    "login": "",
    "password": ""
}'`

Для проверки нотификаций, нужно добавить email в mailgun `Authorized Recipients`.

- Страница аккаунта пользователя `curl --location --request GET 'http://localhost/auth/api/v1/users/' \
--header 'Authorization: Bearer {TOKEN}'`