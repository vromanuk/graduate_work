from http import HTTPStatus
from unittest.mock import Mock
from uuid import uuid4

import jwt
from django.test import RequestFactory, TestCase, override_settings
from mock import patch

from .api.v1.views import StripeWebhookView, SubscriptionApi
from .models import BillingCustomer

USER_ID = uuid4()
JWT_SECRET_KEY = "123"
STRIPE_TEST_SECRET_KEY = "123"
DJSTRIPE_WEBHOOK_SECRET = "123"


class MockProduct(Mock):
    name = "test"


class MockPlan(Mock):
    product = MockProduct()


class MockSubscription(Mock):
    id = 616
    plan = MockPlan()
    cancel_at = 1234567890
    customer = "test_customer"
    status = "cancelled"


class MockCustomer(Mock):
    subscription = MockSubscription()
    has_active_subscription = Mock()
    has_active_subscription.return_value = True


def _get_request(
    url, method="post", jwt_key=JWT_SECRET_KEY, user_id=USER_ID, user_email="@"
):
    factory = RequestFactory()
    token = jwt.encode(
        payload={"sub": str(user_id), "user_email": user_email}, key=jwt_key
    )
    header = {"HTTP_Authorization": f"Bearer {token}"}
    return getattr(factory, method)(url, **header)


class SubscriptionApiTests:
    url = "/api/v1/subscription/"


@override_settings(JWT_SECRET_KEY=JWT_SECRET_KEY)
class PostSubscriptionApiTests(TestCase, SubscriptionApiTests):
    def setUp(self):
        BillingCustomer.objects.create(id=USER_ID)
        self.request = _get_request(url=self.url)

    def test_inactive_subscription(self):
        response = SubscriptionApi.as_view()(self.request)
        self.assertIn("not have active subscription", response.content.decode("utf-8"))

    @patch("stripe.Subscription.modify", return_value=MockSubscription())
    @patch(
        "subscriptions.api.v1.views.BillingCustomer.objects.get",
        return_value=MockCustomer(),
    )
    def test_process_success(self, mock_customer, mock_sub_modify):
        response = SubscriptionApi.as_view()(self.request)
        self.assertEqual(mock_sub_modify.call_count, 1)
        self.assertIn("subscription_id", response.content.decode("utf-8"))


@override_settings(JWT_SECRET_KEY=JWT_SECRET_KEY)
class DeleteSubscriptionApiTests(TestCase, SubscriptionApiTests):
    def setUp(self):
        BillingCustomer.objects.create(id=USER_ID)
        self.request = _get_request(url=self.url, method="delete")

    def test_customer_not_found(self):
        request = _get_request(url=self.url, method="delete", user_id=uuid4())
        response = SubscriptionApi.as_view()(request)
        self.assertIn("customer does not exist", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_inactive_subscription(self):
        response = SubscriptionApi.as_view()(self.request)
        self.assertIn("not have active subscription", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    @patch("stripe.Subscription.modify", return_value=MockSubscription())
    @patch("subscriptions.api.v1.views.JsonResponse")
    @patch("subscriptions.api.v1.views.KafkaService.get_producer")
    @patch(
        "subscriptions.models.BillingCustomer.has_active_subscription",
        return_value=True,
    )
    def test_cancel_subscription(
        self, has_sub_mock, kafka_mock, json_resp_mock, mock_sub_modify
    ):
        response = SubscriptionApi.as_view()(self.request)  # TODO

    @patch("stripe.Subscription.modify", side_effect=Exception)
    @patch(
        "subscriptions.models.BillingCustomer.has_active_subscription",
        return_value=True,
    )
    def test_cancel_exception(self, has_sub_mock, mock_sub_modify):
        response = SubscriptionApi.as_view()(self.request)
        self.assertIn("error", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


@override_settings(STRIPE_TEST_SECRET_KEY=STRIPE_TEST_SECRET_KEY)
@override_settings(DJSTRIPE_WEBHOOK_SECRET=DJSTRIPE_WEBHOOK_SECRET)
class PostStripeWebhookViewTests(TestCase, SubscriptionApiTests):
    url = "/api/v1/webhook/"

    def setUp(self):
        BillingCustomer.objects.create(id=USER_ID)
        factory = RequestFactory()
        header = {"HTTP_STRIPE_SIGNATURE": "test"}
        self.request = factory.post(self.url, **header)

    @patch("stripe.Webhook.construct_event", side_effect=ValueError)
    def test_fail_construct_event(self, mock_construct_event):
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(mock_construct_event.call_count, 1)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    def test_unknown_event(self, mock_construct_event):
        mock_construct_event.return_value = {"type": "test"}
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("stripe.Webhook.construct_event")
    def test_customer_not_found(self, mock_construct_event):
        mock_construct_event.return_value = {
            "type": "invoice_paid",
            "data": {"object": {"customer": None}},
        }
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch("stripe.Webhook.construct_event")
    def test_subscription_not_provided(self, mock_construct_event):
        mock_construct_event.return_value = {
            "type": "invoice_paid",
            "data": {"object": {"customer": 1}},
        }
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch("stripe.Subscription.retrieve", return_value=None)
    @patch("stripe.Webhook.construct_event")
    def test_subscription_not_found(self, mock_construct_event, mock_retrieve):
        mock_construct_event.return_value = {
            "type": "invoice_paid",
            "data": {"object": {"customer": 1, "subscription": 1}},
        }
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch("stripe.Subscription.retrieve", return_value=1)
    @patch("stripe.Webhook.construct_event")
    def test_customer_not_found(self, mock_construct_event, mock_retrieve):
        mock_construct_event.return_value = {
            "type": "invoice_paid",
            "data": {"object": {"customer": uuid4(), "subscription": 1}},
        }
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    @patch("subscriptions.api.v1.views.StripeWebhookView.invoice_paid")
    @patch("stripe.Subscription.retrieve", return_value=1)
    @patch("subscriptions.api.v1.views.KafkaService.get_producer")
    @patch("subscriptions.api.v1.views.BillingCustomer.objects.filter")
    @patch("stripe.Webhook.construct_event")
    def test_process_success(
        self,
        mock_construct_event,
        mock_customer,
        mock_kafka,
        mock_retrieve,
        mock_invoice_paid,
    ):
        mock_construct_event.return_value = {
            "type": "invoice_paid",
            "data": {"object": {"customer": uuid4(), "subscription": 1}},
        }
        response = StripeWebhookView.as_view()(self.request)
        self.assertEqual(response.status_code, HTTPStatus.OK)
