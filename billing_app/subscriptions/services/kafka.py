from django.conf import settings

from confluent_kafka import Producer


class KafkaService:
    @staticmethod
    def get_producer():
        return Producer(**settings.KAFKA_CONFIG)
