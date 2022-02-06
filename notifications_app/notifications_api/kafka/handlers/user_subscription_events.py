from notifications_api.kafka.handlers.base import BaseKafkaHandler
from notifications_api.kafka.schemas.user_subscription_event_schema import (
    UserSubscribedEventSchema,
    UserUnsubscribedEventSchema,
    UserSubscriptionRenewalEventSchema,
)
from notifications_api.kafka.tasks import send_subscription_details_task


class UserSubscribedEventHandler(BaseKafkaHandler):
    topic = "billing_user_subscribed"

    @classmethod
    def handle(cls, body):
        event = UserSubscribedEventSchema.parse_raw(body.value)
        send_subscription_details_task.delay(
            event.email,
            event.notification_transport,
            subject=event.subject,
            content=event.content,
        )


class UserUnsubscribedEventHandler(BaseKafkaHandler):
    topic = "billing_user_unsubscribed"

    @classmethod
    def handle(cls, body):
        event = UserUnsubscribedEventSchema.parse_raw(body.value)
        text_content = f"Привет! Вы успешно отписались 😿. Возвращайтесь снова!"
        send_subscription_details_task.delay(
            event.email,
            event.notification_transport,
            subject=event.subject,
            content=text_content,
        )


class UserSubscriptionRenewalEventHandler(BaseKafkaHandler):
    topic = "billing_subscription_renewal"

    @classmethod
    def handle(cls, body):
        event = UserSubscriptionRenewalEventSchema.parse_raw(body.value)
        text_content = f"Привет! Ваша подписка возобновлена! 😺"
        send_subscription_details_task.delay(
            event.email,
            event.notification_transport,
            subject=event.subject,
            content=text_content,
        )
