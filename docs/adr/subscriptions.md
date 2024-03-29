# Title

Модель Подписок

## Status

принято

## Context

1. Необходимо определиться с моделью биллинга:
- модель подписок
- модель покупки каждого фильма отдельно
2. Где храним информацию о сабскрипшинах?
3. Храним ли данные о карте?

## Decision

1. Была выбрана модель подписок, из-за того, что Stripe позволяет настроить автоматически списания каждый месяц, а также, предоставляет удобную модель создания различных подписок.
2. Храним в сервисе авторизации, в виде отдельной роли или поле `is_subscribed`.
3. Мы не храним эти данные внутри своего сервиса, этим занимается Stripe.

## Consequences

Из-за того, что была выбрана асинхронная модель общения между сервисами, необходимо добавить Kafka Consumer в сервис авторизации, а также, теперь у нас данные Eventual Consistent. Это означает, что после оплаты подписки может пройти некоторое время, когда пользователю станет доступен новый функционал.