from notifications_api.kafka.schemas.base_event_schema import BaseEventSchema


class UserSubscribedEventSchema(BaseEventSchema):
    email: str


class UserUnsubscribedEventSchema(BaseEventSchema):
    email: str
