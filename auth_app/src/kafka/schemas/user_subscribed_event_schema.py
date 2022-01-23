from src.kafka.schemas.base_event_schema import BaseEventSchema


class UserSubscribedEventSchema(BaseEventSchema):
    username: str
