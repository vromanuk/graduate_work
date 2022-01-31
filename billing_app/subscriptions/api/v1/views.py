import json
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Callable, Optional

import djstripe.models
import stripe
from confluent_kafka import Producer
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe.models import Product, Subscription

from subscriptions.api.enums import KAFKA_TOPICS
from subscriptions.models import User
from subscriptions.services import StripeService


def products(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            product.name: [price.human_readable_price for price in product.prices.all()]
            for product in Product.objects.filter(active=True)
        }
    )


def get_user_id():
    return uuid.uuid4()


@csrf_exempt
@require_POST
def create_customer(request: HttpRequest) -> JsonResponse:
    user_id = get_user_id()
    payload = json.loads(request.body)
    try:
        stripe_customer = StripeService.create_customer(email=payload["email"])
        customer = djstripe.models.Customer.sync_from_stripe_data(stripe_customer)
        user, _ = User.objects.get_or_create(id=user_id)
        user.customer = customer
        user.save()
        return JsonResponse(data={"customer": stripe_customer})
    except Exception as error:
        return JsonResponse(data={"error": str(error)}, code=HTTPStatus.FORBIDDEN)


@csrf_exempt
def create_checkout_session(request):
    user_id = get_user_id()
    if request.method == "GET":
        domain_url = "http://localhost:8000/api/v1/"
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancel/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": "price_1KL7emCEmLypaydGDO2u6HvV", "quantity": 1}],
                customer=User.objects.get(id=user_id).customer_id,
            )
            return redirect(checkout_session.url, code=HTTPStatus.SEE_OTHER)
        except Exception as e:
            return JsonResponse({"error": str(e)})


def success(request: HttpRequest) -> HttpResponse:
    return render(request, "success.html")


def cancel(request: HttpRequest) -> HttpResponse:
    return render(request, "cancel.html")


@csrf_exempt
def cancel_subscription(request: HttpRequest) -> JsonResponse:
    if request.method == "DELETE":
        user_id = get_user_id()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "user {0} does not exist".format(user_id)})

        if not user.has_active_subscription():
            return JsonResponse(
                {"error": "user {0} does not have active subscription".format(user_id)}
            )

        try:
            deleted_subscription = stripe.Subscription.modify(
                user.subscription_id, cancel_at_period_end=True
            )
            return JsonResponse({"subscription": deleted_subscription})
        except Exception as e:
            return JsonResponse({"error": str(e), "code": HTTPStatus.FORBIDDEN})
    return JsonResponse({})


@csrf_exempt
def renew_subscription(request: HttpRequest) -> JsonResponse:
    user_id = get_user_id()
    user = User.objects.get(id=user_id)

    if not user.has_active_subscription():
        return JsonResponse(
            {"error": "user {0} does not have an active subscription".format(user_id)}
        )

    if user.subscription.status == "cancelled":
        stripe_subscription = stripe.Subscription.modify(
            user.subscription_id, cancel_at_period_end=False
        )
        user.subscription.status = stripe_subscription.status
        user.save()
        return JsonResponse({"subscription": stripe_subscription})

    return JsonResponse({})


@method_decorator([csrf_exempt, require_POST], name="dispatch")
class StripeWebhookView(View):
    http_allowed_methods = [
        "POST",
    ]

    def event_processor(self, event_type: str) -> Optional[Callable]:
        method_name = event_type.replace(".", "_")
        return getattr(self, method_name, None)

    def send_to_kafka(self, topic, key: str, data: dict):
        kafka_producer = Producer(**settings.KAFKA_CONFIG)
        kafka_producer.produce(topic=topic, value=str(data), key=key)

    def post(self, request: HttpRequest) -> HttpResponse:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        webhook_secret = settings.DJSTRIPE_WEBHOOK_SECRET
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except (ValueError, stripe.error.SignatureVerificationError) as _:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        data_object = event.get("data", {}).get("object", {})
        event_type = event.get("type", "")

        event_processor = self.event_processor(event_type)
        response = HttpResponse(status=HTTPStatus.OK)
        if event_processor:
            response = event_processor(data_object)
        return response

    def checkout_session_completed(self, data_object: dict) -> HttpResponse:
        """
        Payment is successful and the subscription is created.
        Save customer_id and create subscription.
        """

        customer_id = data_object["customer"]
        stripe_subscription = stripe.Subscription.retrieve(data_object["subscription"])

        subscription = Subscription(
            id=stripe_subscription.id,
            customer_id=customer_id,
            current_period_start=datetime.fromtimestamp(
                stripe_subscription.current_period_start
            ),
            current_period_end=datetime.fromtimestamp(
                stripe_subscription.current_period_end
            ),
            status=stripe_subscription.status,
        )
        subscription.save()

        user = User.objects.get(customer_id=customer_id)
        user.subscription = subscription
        user.save()

        self.send_to_kafka(
            topic=KAFKA_TOPICS.CHECKOUT_SESSION_COMPLETED.value,
            key=f"{KAFKA_TOPICS.CHECKOUT_SESSION_COMPLETED.value}_{subscription.id}_{user.id}",
            data={
                "user_id": user.id,
                "customer_id": customer_id,
            },
        )

        return HttpResponse(status=HTTPStatus.OK)

    def invoice_paid(self, data_object: dict):
        """
        Subscription is being paid.
        """
        customer_id = data_object.get("customer", None)
        if not customer_id:
            # customer doesn't exist
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription_object = data_object.get("subscription", None)
        if not subscription_object:
            # subscription is not provied
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        stripe_subscription = stripe.Subscription.retrieve(subscription_object)

        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start
        ),
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        ),
        subscription.save()

        user = User.objects.filter(customer_id=customer_id).first()
        if not user:
            # user does not exist
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        self.send_to_kafka(
            topic=KAFKA_TOPICS.INVOICE_PAID.value,
            key=f"{KAFKA_TOPICS.INVOICE_PAID.value}_{subscription.id}_{user.id}",
            data={
                "user_id": user.id,
                "customer_id": customer_id,
            },
        )
        return HttpResponse(status=HTTPStatus.OK)

    def invoice_payment_failed(self, data_object: dict) -> HttpResponse:
        """
        Payment failed.
        """
        customer_id = data_object.get("customer", None)
        if not customer_id:
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription_object = data_object.get("subscription", None)
        if not subscription_object:
            # subscription is not provied
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        stripe_subscription = stripe.Subscription.retrieve(subscription_object)

        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.save()

        user = User.objects.filter(customer_id=customer_id).first()
        if not user:
            # user does not exist
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        self.send_to_kafka(
            topic=KAFKA_TOPICS.INVOICE_PAYMENT_FAILED.value,
            key=f"{KAFKA_TOPICS.INVOICE_PAYMENT_FAILED.value}_{subscription.id}_{user.id}",
            data={
                "user_id": user.id,
                "customer_id": customer_id,
            },
        )

        return HttpResponse(status=HTTPStatus.OK)


stripe_webhook = StripeWebhookView.as_view()
