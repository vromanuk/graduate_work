from notifications_api.kafka.schemas.base_event_schema import BaseEventSchema


class UserSubscribedEventSchema(BaseEventSchema):
    username: str
    email: str


class UserUnsubscribedEventSchema(BaseEventSchema):
    username: str
    email: str
