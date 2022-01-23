from src.kafka.handlers.user_subscribed_event import UserSubscribedEventHandler
from src.kafka.registry import EventRegistry

event_registry = EventRegistry()

event_registry.register(UserSubscribedEventHandler)
