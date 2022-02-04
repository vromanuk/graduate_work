from http import HTTPStatus

from django.test import TestCase, override_settings
from mock import Mock, patch

from ..api.v1.views import create_checkout_session
from ..models import BillingCustomer
from .base import _get_request, settings


@override_settings(STRIPE_TEST_SECRET_KEY=settings.STRIPE_TEST_SECRET_KEY)
@override_settings(JWT_SECRET_KEY=settings.JWT_SECRET_KEY)
class CreateCheckoutSessionTests(TestCase):
    url = "/api/v1/checkout/"

    def setUp(self):
        BillingCustomer.objects.create(id=settings.USER_ID)
        self.request = _get_request(url=self.url, method="get")

    @patch("stripe.checkout.Session.create", return_value=Mock(url="kek"))
    def test_process_success(self, mock_create):
        response = create_checkout_session(self.request)
        self.assertIn("kek", response.content.decode("utf-8"))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @patch("stripe.checkout.Session.create", side_effect=Exception)
    def test_exception(self, mock_create):
        response = create_checkout_session(self.request)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
