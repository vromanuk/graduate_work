from functools import lru_cache

from confluent_kafka import Consumer

from src.config import Config


@lru_cache()
def get_kafka_consumer() -> Consumer:
    conf = {
        "bootstrap.servers": f"{Config.KAFKA_HOST}:{Config.KAFKA_PORT}",
        "group.id": "user_subscription_group",
        "auto.offset.reset": "smallest",
        "enable.auto.commit": False,
    }

    return Consumer(conf)
