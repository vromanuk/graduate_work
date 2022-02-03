from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.products),
    path("checkout/", views.create_checkout_session),
    path("success/", views.success),
    path("cancel/", views.cancel),
    path("customer/", views.customer_view),
    path("subscription/", views.subscription_view),
    path("webhook/", views.stripe_webhook),
    path("smoke/", views.smoke),
]
