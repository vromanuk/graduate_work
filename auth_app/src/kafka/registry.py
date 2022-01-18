from dataclasses import dataclass, field
from typing import Dict, Type

from src.kafka.handlers.base import BaseKafkaHandler


@dataclass(frozen=True)
class EventRegistry:
    topic_dispatcher: Dict[str, Type[BaseKafkaHandler]] = field(default_factory=dict)

    def register(self, handler: Type[BaseKafkaHandler]) -> None:
        self.topic_dispatcher[handler.topic] = handler
