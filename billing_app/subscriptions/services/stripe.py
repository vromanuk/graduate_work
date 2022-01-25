import stripe
from django.conf import settings
from stripe.api_resources.customer import Customer
from stripe.api_resources.subscription import Subscription


class StripeService:
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    @staticmethod
    def create_customer(email: str, payment_method: str = None) -> Customer:
        return stripe.Customer.create(
            email=email,
            payment_method=payment_method,
            invoice_settings={"default_payment_method": payment_method},
        )

    @staticmethod
    def create_subscription(customer_id: str, price_id: str) -> Subscription:
        return stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )
