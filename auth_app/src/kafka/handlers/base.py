import abc


class BaseKafkaHandler(abc.ABC):
    __slots__ = ("topic",)

    topic: str

    @classmethod
    @abc.abstractmethod
    def handle(cls, body):
        ...
