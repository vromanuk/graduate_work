from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from notifications_api.emails.constants import NotificationTransport


class BaseEventSchema(BaseModel):
    notification_transport: str = NotificationTransport.EMAIL.value
    subject: str = ""
    content: str = ""
    user_id: Optional[UUID] = None
