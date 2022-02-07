from uuid import UUID

import djstripe
import stripe
from django.db import models


class BillingCustomer(models.Model):
    id = models.UUIDField(primary_key=True)
    email = models.EmailField()
    customer = models.ForeignKey(
        "djstripe.Customer",
        to_field="id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    subscription = models.ForeignKey(
        "djstripe.Subscription",
        to_field="id",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    @classmethod
    def from_stripe_customer(
        cls, user_id: UUID, email: str, stripe_customer: stripe.Customer
    ) -> "BillingCustomer":
        djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(
            stripe_customer
        )
        customer = cls.objects.create(
            id=user_id, email=email, customer=djstripe_customer
        )
        customer.save()
        return customer

    def has_subscription(self) -> bool:
        """
        Return True if the user has a subscription. The subscription status does not matter.
        """
        return self.subscription is not None

    def has_active_subscription(self) -> bool:
        """
        Return True if the user has an active subscription.
        """
        return self.has_subscription() and self.subscription.status == "active"
