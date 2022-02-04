from enum import Enum


class KAFKA_TOPICS(Enum):
    USER_SUBSCRIBED = "billing_user_subscribed"
    USER_UNSUBSCRIBED = "billing_user_unsubscribed"
    INVOICE_PAID = "billing_invoice_paid"
    INVOICE_PAYMENT_FAILED = "billing_invoice_payment_failed"

    @classmethod
    def get_topic_by_event(cls, event_type: str) -> str:
        return {
            "checkout.session.completed": KAFKA_TOPICS.USER_SUBSCRIBED.value,
            "invoice.paid": KAFKA_TOPICS.INVOICE_PAID.value,
            "invoice.payment.failed": KAFKA_TOPICS.INVOICE_PAYMENT_FAILED.value,
        }.get(event_type, "")
