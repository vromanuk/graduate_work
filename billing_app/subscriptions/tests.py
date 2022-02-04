from http import HTTPStatus
from unittest.mock import Mock
from uuid import uuid4

import jwt
from django.test import RequestFactory, TestCase, override_settings
from mock import patch

from .api.v1.views import SubscriptionApi
from .models import BillingCustomer

USER_ID = uuid4()
JWT_SECRET_KEY = "123"


class MockProduct(Mock):
    name = "test"


class MockPlan(Mock):
    product = MockProduct()


class MockSubscription(Mock):
    plan = MockPlan()
    cancel_at = 1234567890


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
    @patch("subscriptions.api.v1.views.KafkaService")
    @patch(
        "subscriptions.models.BillingCustomer.has_active_subscription",
        return_value=True,
    )
    def test_cancel_subscription(
            self, has_sub_mock, kafka_mock, json_resp_mock, stripe_mock
    ):
        response = SubscriptionApi.as_view()(self.request)  # TODO

    @patch("stripe.Subscription.modify", side_effect=Exception)
    @patch(
        "subscriptions.models.BillingCustomer.has_active_subscription",
        return_value=True,
    )
    def test_cancel_subscription(self, has_sub_mock, stripe_mock):
        response = SubscriptionApi.as_view()(self.request)
        self.assertIn("error", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
