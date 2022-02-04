from django.contrib import admin

from subscriptions.models import BillingCustomer


@admin.register(BillingCustomer)
class BillingCustomerAdmin(admin.ModelAdmin):
    pass
