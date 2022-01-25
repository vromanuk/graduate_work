from notifications_api.kafka.handlers.user_registered_event import (
    UserRegisteredEventHandler,
)
from notifications_api.kafka.handlers.user_subscription_events import UserSubscribedEventHandler, \
    UserUnsubscribedEventHandler
from notifications_api.kafka.registry import EventRegistry

event_registry = EventRegistry()

event_registry.register(UserRegisteredEventHandler)
event_registry.register(UserSubscribedEventHandler)
event_registry.register(UserUnsubscribedEventHandler)
