from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.products),
    path("checkout/", views.create_checkout_session),
    path("customer/", views.create_customer),
    path("success/", views.success),
    path("cancel/", views.cancel),
    path("cancel-subscription/", views.cancel_subscription),
    path("webhook/", views.stripe_webhook),
]
