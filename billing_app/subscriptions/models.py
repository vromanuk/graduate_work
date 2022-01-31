from django.db import models


class Customer(models.Model):
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

    def has_active_subscription(self) -> bool:
        return self.subscription is not None
