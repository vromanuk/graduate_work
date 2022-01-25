import json
import logging

from src.kafka.handlers.base import BaseKafkaHandler
from src.kafka.schemas.user_subscription_event_schemas import (
    UserSubscribedEventSchema, UserUnsubscribedEventSchema)
from src.services.users_service import UserService

logger = logging.getLogger(__name__)


class UserSubscribedEventHandler(BaseKafkaHandler):
    topic = "user_subscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserSubscribedEventSchema(msg["user_id"], msg["subscription"])
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
    topic = "user_unsubscribed"

    @classmethod
    def handle(cls, body):
        msg = json.loads(body.value())
        event = UserUnsubscribedEventSchema(msg["user_id"])
        updated = UserService.reset_role(user_id=event.user_id, default=True)
        if updated:
            logger.info(f"Subscription for {event.user_id} was successfully cancelled")
        else:
            logger.error(f"Subscription for {event.user_id} wasn't cancelled")
