from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UserSubscribedEventSchema:
    user_id: UUID
    subscription: str


@dataclass(frozen=True)
class UserUnsubscribedEventSchema:
    user_id: UUID
