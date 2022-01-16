from notifications_api.kafka.schemas.base_event_schema import BaseEventSchema


class UserRegisteredEventSchema(BaseEventSchema):
    username: str
    email: str
