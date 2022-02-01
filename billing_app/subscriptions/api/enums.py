from enum import Enum


class KAFKA_TOPICS(Enum):
    USER_SUBSCRIBED = "billing_user_subscribed"
    USER_UNSUBSCRIBED = "billing_user_unsubscribed"
    INVOICE_PAID = "billing_invoice_paid"
    INVOICE_PAYMENT_FAILED = "billing_invoice_payment_failed"

