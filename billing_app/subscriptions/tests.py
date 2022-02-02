from django.test import TestCase
from unittest.mock import Mock

from mock import patch
from .models import BillingCustomer
from uuid import uuid4
from .api.v1 import views
from django.http.request import HttpRequest

USER_ID = uuid4()


class MockProduct(Mock):
    name = 'test'


class MockPlan(Mock):
    product = MockProduct()


class MockSubscription(Mock):
    plan = MockPlan()
    cancel_at = 1234567890


class CancelSubscriptionTests(TestCase):

    def setUp(self):
        self.user = BillingCustomer.objects.create(id=USER_ID)
        self.request = HttpRequest()
        self.request.method = "DELETE"
        self.request.user_email = "test@test.ru"

    @patch("subscriptions.api.v1.views.get_user_id", return_value=uuid4())
    def test_customer_not_found(self, get_user_id_mock):
        res = views.cancel_subscription(self.request)
        self.assertIn('does not exist', res.content.decode('utf-8'))

    @patch("subscriptions.models.BillingCustomer.has_active_subscription", return_value=False)
    @patch("subscriptions.api.v1.views.get_user_id", return_value=USER_ID)
    def test_no_active_subscription(self, get_user_id_mock, has_sub_mock):
        res = views.cancel_subscription(self.request)
        self.assertIn('not have active subscription', res.content.decode('utf-8'))

    @patch("stripe.Subscription.modify", return_value=MockSubscription())
    @patch("subscriptions.api.v1.views.JsonResponse")
    @patch("subscriptions.api.v1.views.KafkaService")
    @patch("subscriptions.models.BillingCustomer.has_active_subscription", return_value=True)
    @patch("subscriptions.api.v1.views.get_user_id", return_value=USER_ID)
    def test_cancel_subscription(self, get_user_id_mock, has_sub_mock, kafka_mock, json_resp_mock, stripe_mock):
        res = views.cancel_subscription(self.request)
