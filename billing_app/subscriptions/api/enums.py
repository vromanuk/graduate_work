from enum import Enum


class KAFKA_TOPICS(Enum):
    CHECKOUT_SESSION_COMPLETED = "billing_checkout_session_completed"
    INVOICE_PAID = "billing_invoice_paid"
    INVOICE_PAYMENT_FAILED = "billing_invoice_payment_failed"
