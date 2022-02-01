from uuid import UUID

import djstripe
import stripe
from django.db import models


class BillingCustomer(models.Model):
    id = models.UUIDField(primary_key=True)
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
        cls, user_id: UUID, stripe_customer: stripe.Customer
    ) -> "BillingCustomer":
        djstripe_customer = djstripe.models.Customer.sync_from_stripe_data(
            stripe_customer
        )
        customer = cls.objects.create(id=user_id, customer=djstripe_customer)
        customer.save()
        return customer

    def has_active_subscription(self) -> bool:
        return self.subscription is not None
