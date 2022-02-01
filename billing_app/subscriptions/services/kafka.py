from confluent_kafka import Producer
from django.conf import settings


class KafkaService:
    @classmethod
    def get_producer(cls):
        return Producer(**settings.KAFKA_CONFIG)

