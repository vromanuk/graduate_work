from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class UserSubscribedEventSchema:
    user_id: UUID
    subscription: str
    subscription_expire_date: Optional[datetime] = None


@dataclass(frozen=True)
class UserUnsubscribedEventSchema:
    user_id: UUID


@dataclass(frozen=True)
class UserSubscriptionRenewalEventSchema:
    user_id: UUID
    email: str
