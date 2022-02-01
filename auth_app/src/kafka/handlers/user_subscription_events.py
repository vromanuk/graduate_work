import datetime
import json
import logging

from src.kafka.handlers.base import BaseKafkaHandler
from src.kafka.schemas.user_subscription_event_schemas import (
    UserSubscribedEventSchema,
    UserUnsubscribedEventSchema,
)
from src.services.users_service import UserService

logger = logging.getLogger(__name__)


class UserSubscribedEventHandler(BaseKafkaHandler):
    topic = "billing_user_subscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserSubscribedEventSchema(
            user_id=msg["user_id"],
            subscription=msg["subscription"],
            subscription_expire_date=msg.get("subscription_expire_date"),
        )
        UserService.update_subscription(
            user_id=event.user_id,
            expire_date=event.subscription_expire_date,
            is_active=True,
            subscription_name=event.subscription,
        )
        updated = UserService.update_role(
            user_id=event.user_id, subscription=event.subscription
        )
        if updated:
            logger.info(
                f"Subscription: {event.subscription} for {event.user_id} was successfully updated"
            )
        else:
            logger.error(
                f"Subscription: {event.subscription} for {event.user_id} wasn't updated"
            )


class UserUnsubscribedEventHandler(BaseKafkaHandler):
    topic = "billing_user_unsubscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserUnsubscribedEventSchema(msg["user_id"])
        UserService.update_subscription(
            user_id=event.user_id, expire_date=datetime.datetime.now(), is_active=False
        )
        updated = UserService.reset_role(user_id=event.user_id, default=True)
        if updated:
            logger.info(f"Subscription for {event.user_id} was successfully cancelled")
        else:
            logger.error(f"Subscription for {event.user_id} wasn't cancelled")