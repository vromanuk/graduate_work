import json
import uuid
from datetime import datetime

from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe.models import Customer, Product, Subscription

from subscriptions.models import User
from subscriptions.services.stripe import StripeService


def products(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            product.name: [price.human_readable_price for price in product.prices.all()]
            for product in Product.objects.filter(active=True)
        }
    )


def get_user_id_email():
    # todo: we should get this data from a JWT
    return uuid.uuid4(), "joe@gmail.com"


# todo: only authenticated users
@csrf_exempt
@require_POST
@transaction.atomic
def subscribe(request: HttpRequest) -> JsonResponse:
    user_id, email = get_user_id_email()  # todo: stub
    payload = json.loads(request.body.decode())

    user, _ = User.objects.get_or_create(id=user_id)
    if user.has_active_subscription():
        return JsonResponse(
            data={
                "message": "The user already subscribed",
                "user_id": user.id,
                "customer_id": user.customer_id,
                "subscription_id": user.subscription_id,
            }
        )

    if not user.customer_id:
        customer = StripeService.create_customer(
            email, payment_method=(payload["payment_method_id"])
        )
        djstripe_customer = Customer.sync_from_stripe_data(customer)
    else:
        djstripe_customer = Customer.objects.get(id=user.customer_id)

    subscription = StripeService.create_subscription(
        djstripe_customer.id, payload["price_id"]
    )

    # todo: the next line should work, but it doesn't. It looks like a djstripe bug.
    # djstripe_subscription = Subscription.sync_from_stripe_data(subscription)

    # todo: workaround for the problem above
    djstripe_subscription = Subscription(
        id=subscription.id,
        customer_id=djstripe_customer.id,
        current_period_start=datetime.fromtimestamp(subscription.current_period_start),
        current_period_end=datetime.fromtimestamp(subscription.current_period_end),
    )
    djstripe_subscription.save()

    user.customer = djstripe_customer
    user.subscription = djstripe_subscription
    user.save()

    return JsonResponse(
        data={
            "message": "Ok",
            "user_id": user.id,
            "customer_id": user.customer_id,
            "subscription_id": user.subscription_id,
        }
    )
