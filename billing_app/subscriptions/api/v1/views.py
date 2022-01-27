import json
import uuid
from datetime import datetime
from typing import Optional, Callable
from http import HTTPStatus

import djstripe.models
import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe.models import Product, Subscription

from subscriptions.models import User
from subscriptions.services import StripeService, KafkaService


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
            user, _ = User.objects.get_or_create(id=user_id)
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancel/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": "price_1KL7emCEmLypaydGDO2u6HvV", "quantity": 1}],
                customer=user.customer_id,
            )
            return redirect(checkout_session.url, code=HTTPStatus.SEE_OTHER)
        except Exception as e:
            return JsonResponse({"error": str(e)})


def success(request: HttpRequest) -> HttpResponse:
    return render(request, "success.html")


def cancel(request: HttpRequest) -> HttpResponse:
    return render(request, "cancel.html")


@method_decorator([csrf_exempt, require_POST], name='dispatch')
class StripeWebhookView(View):
    http_allowed_methods = ["POST", ]
    kafka_producer = KafkaService.get_producer()

    def event_processor(self, event_type: str) -> Optional[Callable]:
        method_name = event_type.replace(".", "_")
        return getattr(self, method_name, None)

    def send_to_kafka(self, topic, key: str, value: str):
        self.kafka_producer.produce(topic=topic, value=value, key=key)

    def post(self, request: HttpRequest) -> HttpResponse:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        webhook_secret = settings.DJSTRIPE_WEBHOOK_SECRET
        payload = request.body
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except (ValueError, stripe.error.SignatureVerificationError) as _:
            return HttpResponse(status=HTTPStatus.BAD_REQUEST)

        data_object = event.get("data", {}).get("object", {})
        event_type = event.get("type", "")

        event_processor = self.event_processor(event_type)
        if event_processor:
            event_processor(data_object)
        return HttpResponse(status=HTTPStatus.OK)

    def checkout_session_completed(self, data_object: dict):
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

        # TODO: refactoring
        kafka_topic = "billing_checkout_session_completed"
        kafka_key = f"billing_{subscription.id}_{user.id}"
        kafka_value = str({
            'user_id': user.id,
            'customer_id': customer_id,
        })

        self.send_to_kafka(topic=kafka_topic, key=kafka_key, value=kafka_value)

    # TODO
    def invoice_upcoming(self, data_object: dict):
        """
        Time to pay.
        """
        pass

    # TODO
    def invoice_paid(self, data_object: dict):
        """
        Subscription is paid.
        """
        pass

    # TODO
    def invoice_payment_failed(self, data_object: dict):
        """
        Payment failed.
        """
        pass


stripe_webhook = StripeWebhookView.as_view()

