# flake8: noqa

import django

django.setup()
from notifications_api.kafka.consumer import get_kafka_consumer
from notifications_api.kafka.events import event_registry


def consume():
    consumer = get_kafka_consumer()

    consumer.subscribe(event_registry.topic_dispatcher.keys())

    for message in consumer:
        event_registry.topic_dispatcher[message.topic].handle(message)


if __name__ == "__main__":
    consume()
