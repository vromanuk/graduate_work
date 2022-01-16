from functools import lru_cache

import environ
from kafka import KafkaConsumer

env = environ.Env()


@lru_cache()
def get_kafka_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        bootstrap_servers=[f"{env.str('KAFKA_HOST')}:{env.str('KAFKA_PORT')}"],
    )
