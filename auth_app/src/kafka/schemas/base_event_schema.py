from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class BaseEventSchema:
    subject: str = ""
    content: str = ""
    user_id: Optional[UUID] = None
