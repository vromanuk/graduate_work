import json
import uuid
from datetime import datetime
from http import HTTPStatus
from typing import Callable, Optional

import stripe
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe.models import Product, Subscription

from subscriptions.api.constants import (
    SESSION_COMPLETED,
    USER_SUBSCRIBED,
    USER_SUBSCRIPTION_RENEWAL,
    USER_UNSUBSCRIBED,
)
from subscriptions.api.utils import token_required
from subscriptions.models import BillingCustomer
from subscriptions.services import KafkaService, StripeService


def get_user_id():
    return uuid.uuid4()


def products(request: HttpRequest) -> JsonResponse:
    return JsonResponse(
        {
            product.name: [price.human_readable_price for price in product.prices.all()]
            for product in Product.objects.filter(active=True)
        }
    )


@token_required
def smoke(request):
    return JsonResponse(data={"msg": "OK", "user": request.user_id})


@csrf_exempt
@token_required
def create_checkout_session(request):
    if request.method == "GET":
        domain_url = "http://localhost/api/v1/"
        # domain_url = settings.BASE_API_URL
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=domain_url + "cancel/",
                payment_method_types=["card"],
                mode="subscription",
                line_items=[{"price": "price_1KL7emCEmLypaydGDO2u6HvV", "quantity": 1}],
                customer=BillingCustomer.objects.get(id=request.user_id).customer_id,
            )
            # return redirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)
            return JsonResponse({"checkout_session_url": checkout_session.url})
        except Exception as e:
            return JsonResponse(
                {"message": str(e), "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )


def success(request: HttpRequest) -> HttpResponse:
    return render(request, "success.html")


def cancel(request: HttpRequest) -> HttpResponse:
    return render(request, "cancel.html")


@method_decorator([csrf_exempt, token_required], name="dispatch")
class Customer(View):
    def post(self, request: HttpRequest) -> JsonResponse:
        try:
            queryset = BillingCustomer.objects.filter(id=request.user_id)
            if not queryset.exists():
                stripe_customer = StripeService.create_customer(request.user_email)
                customer = BillingCustomer.from_stripe_customer(
                    request.user_id, request.user_email, stripe_customer
                )
            else:
                customer = queryset.first()
            return JsonResponse(
                {
                    "message": "Ok",
                    "user_id": request.user_id,
                    "customer_id": customer.customer_id,
                }
            )
        except Exception as error:
            return JsonResponse(
                data={"message": str(error), "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )


@method_decorator([csrf_exempt, token_required], name="dispatch")
class SubscriptionApi(View):
    http_method_names = ["post", "delete"]

    def post(self, request: HttpRequest) -> JsonResponse:
        billing_customer = BillingCustomer.objects.get(id=request.user_id)

        if not billing_customer.has_subscription():
            return JsonResponse(
                {
                    "message": "user does not have subscription",
                    "user_id": request.user_id,
                    "customer_id": billing_customer.customer_id,
                    "subscription_id": billing_customer.subscription_id,
                },
                status=HTTPStatus.FORBIDDEN,
            )

        # If the user's subscription has cancelled, renew it.
        if billing_customer.subscription.cancel_at_period_end:
            stripe_subscription = stripe.Subscription.modify(
                billing_customer.subscription_id, cancel_at_period_end=False
            )
            billing_customer.subscription.cancel_at_period_end = False
            billing_customer.subscription.save()

            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_SUBSCRIPTION_RENEWAL,
                key=f"{USER_SUBSCRIPTION_RENEWAL}_{billing_customer.subscription_id}_{request.user_id}",
                value=json.dumps(
                    {
                        "user_id": str(request.user_id),
                        "email": billing_customer.email,
                    }
                ),
            )
            kafka_producer.flush()

            return JsonResponse(
                {
                    "message": "Ok",
                    "user_id": request.user_id,
                    "customer_id": stripe_subscription.customer,
                    "subscription_id": stripe_subscription.id,
                }
            )

        # User's subscription is active, there's nothing to renew.
        return JsonResponse(
            {
                "message": "user subscription is active",
                "user_id": request.user_id,
                "customer_id": billing_customer.customer_id,
                "subscription_id": billing_customer.subscription_id,
            },
            status=HTTPStatus.BAD_REQUEST,
        )

    def delete(self, request: HttpRequest) -> JsonResponse:
        queryset = BillingCustomer.objects.filter(id=request.user_id)
        if not queryset.exists():
            return JsonResponse(
                {"message": "customer does not exist", "user_id": request.user_id},
                status=HTTPStatus.FORBIDDEN,
            )

        billing_customer = queryset.first()
        if not billing_customer.has_active_subscription():
            return JsonResponse(
                {
                    "message": "customer does not have active subscription",
                    "user_id": request.user_id,
                },
                status=HTTPStatus.FORBIDDEN,
            )

        if billing_customer.subscription.cancel_at_period_end:
            return JsonResponse(
                {
                    "message": "user has already cancelled subscription",
                    "user_id": request.user_id,
                }
            )

        try:
            deleted_subscription = stripe.Subscription.modify(
                billing_customer.subscription_id, cancel_at_period_end=True
            )
            product = stripe.Product.retrieve(deleted_subscription["plan"]["product"])
            billing_customer.subscription.cancel_at_period_end = (
                deleted_subscription.cancel_at_period_end
            )
            billing_customer.subscription.save()

            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_UNSUBSCRIBED,
                key=f"{USER_UNSUBSCRIBED}_{deleted_subscription.id}_{request.user_id}",
                value=json.dumps(
                    {
                        "user_id": str(request.user_id),
                        "subscription": product["name"],
                        "email": billing_customer.email,
                    }
                ),
            )
            kafka_producer.flush()
            return JsonResponse({"subscription": deleted_subscription})
        except Exception as error:
            return JsonResponse({"error": str(error)}, status=HTTPStatus.FORBIDDEN)


@method_decorator([csrf_exempt, require_POST], name="dispatch")
class StripeWebhookView(View):
    http_allowed_methods = ["POST"]

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

        subscription_updater = self.subscription_updater(event_type)
        if not subscription_updater:
            return HttpResponse(status=HTTPStatus.OK)

        customer_id = data_object.get("customer", None)
        if not customer_id:
            # customer is not provided
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription_object = data_object.get("subscription", None)
        if not subscription_object:
            # subscription is not provided
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        stripe_subscription = stripe.Subscription.retrieve(subscription_object)
        if not stripe_subscription:
            # stripe subscription is not found
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        product = stripe.Product.retrieve(stripe_subscription["plan"]["product"])

        billing_user = BillingCustomer.objects.filter(customer_id=customer_id).first()
        if not billing_user:
            # user does not exist
            return HttpResponse(status=HTTPStatus.NOT_FOUND)

        subscription = subscription_updater(customer_id, stripe_subscription)
        billing_user.subscription = subscription
        billing_user.save()

        if event_type == SESSION_COMPLETED:
            kafka_producer = KafkaService.get_producer()
            kafka_producer.produce(
                topic=USER_SUBSCRIBED,
                key=f"{USER_SUBSCRIBED}_{stripe_subscription.id}_{billing_user.id}",
                value=json.dumps(
                    {
                        "user_id": str(billing_user.id),
                        "subscription": product["name"],
                        "email": billing_user.email,
                        "subscription_expire_date": str(
                            subscription.current_period_end
                        ),
                    }
                ),
            )
            kafka_producer.flush()
        return HttpResponse(status=HTTPStatus.OK)

    def subscription_updater(self, event_type: str) -> Optional[Callable]:
        """
        Update subscription based on different subscription events.
        Parameter event_type is subscription's event name e.g. invoice.paid.
        We get a corresponding method by replacing dots with underscores.
        """
        method_name = event_type.replace(".", "_")
        return getattr(self, method_name, None)

    def checkout_session_completed(
        self, customer_id, stripe_subscription
    ) -> Subscription:
        """
        Payment is successful and the subscription is created.
        Save customer_id and create subscription.
        """
        subscription = Subscription.objects.create(
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
        return subscription

    def invoice_paid(self, customer_id, stripe_subscription) -> Subscription:
        """
        Subscription is being paid.
        """
        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.current_period_start = datetime.fromtimestamp(
            stripe_subscription.current_period_start
        )
        subscription.current_period_end = datetime.fromtimestamp(
            stripe_subscription.current_period_end
        )
        subscription.save(
            update_fields=[
                "status",
                "current_period_start",
                "current_period_end",
            ]
        )
        return subscription

    def invoice_payment_failed(self, customer_id, stripe_subscription) -> Subscription:
        """
        Payment failed.
        """
        subscription, _ = Subscription.objects.get_or_create(
            id=stripe_subscription.id, customer_id=customer_id
        )
        subscription.status = stripe_subscription.status
        subscription.save()
        return subscription


customer_view = Customer.as_view()
subscription_view = SubscriptionApi.as_view()
stripe_webhook = StripeWebhookView.as_view()
