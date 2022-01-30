import enum


@enum.unique
class SubscriptionStatus(enum.Enum):
    FREE = "free"
    ACTIVE = "active"
    IDLE = "idle"
