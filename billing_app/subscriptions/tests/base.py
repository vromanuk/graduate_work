from unittest.mock import Mock
from uuid import uuid4

import jwt
from django.test import RequestFactory


class MockSettings:
    USER_ID = uuid4()
    JWT_SECRET_KEY = "123"
    STRIPE_TEST_SECRET_KEY = "123"
    DJSTRIPE_WEBHOOK_SECRET = "123"


settings = MockSettings()


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
    url,
    method="post",
    jwt_key=settings.JWT_SECRET_KEY,
    user_id=settings.USER_ID,
    user_email="@",
):
    factory = RequestFactory()
    token = jwt.encode(
        payload={"sub": str(user_id), "user_email": user_email}, key=jwt_key
    )
    header = {"HTTP_Authorization": f"Bearer {token}"}
    return getattr(factory, method)(url, **header)
