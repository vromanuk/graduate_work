from http import HTTPStatus
from uuid import uuid4

from django.test import RequestFactory, TestCase, override_settings
from mock import patch

from ..api.v1.views import StripeWebhookView
from ..models import BillingCustomer
from .base import settings


@override_settings(STRIPE_TEST_SECRET_KEY=settings.STRIPE_TEST_SECRET_KEY)
@override_settings(DJSTRIPE_WEBHOOK_SECRET=settings.DJSTRIPE_WEBHOOK_SECRET)
class PostStripeWebhookViewTests(TestCase):
    url = "/api/v1/webhook/"

    def setUp(self):
        BillingCustomer.objects.create(id=settings.USER_ID)
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
