from http import HTTPStatus
from uuid import uuid4

from django.test import TestCase, override_settings
from mock import patch

from ..api.v1.views import SubscriptionApi
from ..models import BillingCustomer
from .base import MockCustomer, MockSubscription, _get_request, settings


class SubscriptionApiTests:
    url = "/api/v1/subscription/"


@override_settings(JWT_SECRET_KEY=settings.JWT_SECRET_KEY)
class PostSubscriptionApiTests(TestCase, SubscriptionApiTests):
    def setUp(self):
        BillingCustomer.objects.create(id=settings.USER_ID)
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


@override_settings(JWT_SECRET_KEY=settings.JWT_SECRET_KEY)
class DeleteSubscriptionApiTests(TestCase, SubscriptionApiTests):
    def setUp(self):
        BillingCustomer.objects.create(id=settings.USER_ID)
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
