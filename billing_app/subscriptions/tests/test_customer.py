from http import HTTPStatus
from uuid import uuid4

from django.test import TestCase, override_settings
from mock import patch

from ..api.v1.views import Customer
from ..models import BillingCustomer
from .base import _get_request, settings


@override_settings(JWT_SECRET_KEY=settings.JWT_SECRET_KEY)
class PostCustomerTests(TestCase):
    url = "/api/v1/customer/"

    def setUp(self):
        BillingCustomer.objects.create(id=settings.USER_ID)
        self.request = _get_request(url=self.url)

    def test_process_success(self):
        response = Customer.as_view()(self.request)
        self.assertIn(str(settings.USER_ID), response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch(
        "subscriptions.api.v1.views.StripeService.create_customer",
        side_effect=Exception,
    )
    def test_exception(self, mock_create_customer):
        request = _get_request(url=self.url, user_id=uuid4())
        response = Customer.as_view()(request)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
