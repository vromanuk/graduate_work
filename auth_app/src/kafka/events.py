from src.kafka.handlers.user_subscription_events import (
    UserSubscribedEventHandler, UserUnsubscribedEventHandler, UserSubscriptionRenewalEventHandler)
from src.kafka.registry import EventRegistry

event_registry = EventRegistry()

event_registry.register(UserSubscribedEventHandler)
event_registry.register(UserUnsubscribedEventHandler)
event_registry.register(UserSubscriptionRenewalEventHandler)
