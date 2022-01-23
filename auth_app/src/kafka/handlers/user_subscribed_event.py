from src.kafka.handlers.base import BaseKafkaHandler
from src.kafka.schemas.user_subscribed_event_schema import \
    UserSubscribedEventSchema


class UserSubscribedEventHandler(BaseKafkaHandler):
    topic = "user_subscribed"

    @classmethod
    def handle(cls, body):
        print(f"topic: {body.topic()}; value:{body.value()}")
        # event = UserSubscribedEventSchema(body.value())
        # update user subscription info
