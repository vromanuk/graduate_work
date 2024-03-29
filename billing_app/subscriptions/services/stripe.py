import stripe
from django.conf import settings
from stripe.api_resources.customer import Customer


class StripeService:
    stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    @staticmethod
    def create_customer(email: str) -> Customer:
        return stripe.Customer.create(email=email)
