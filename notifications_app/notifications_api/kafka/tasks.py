from celery import shared_task

from notifications_api.apps.users.services.user import UserService
from notifications_api.emails.constants import (
    TRANSPORT_DISPATCHER,
    NotificationTransport,
)
from notifications_api.emails.services.transport_service import TransportService


@shared_task
def send_welcome_letter_task(
    username: str,
    send_to: str,
    transport: str = NotificationTransport.EMAIL.value,
    **kwargs,
) -> None:
    notification_transport = TRANSPORT_DISPATCHER[transport]
    transport_service = TransportService(notification_transport)
    transport_service.send_welcome_letter(
        username, send_to, subject=kwargs["subject"], content=kwargs["content"]
    )


@shared_task
def save_new_user_to_db_task(username: str, email: str) -> None:
    UserService.create_user(username, email)


@shared_task
def send_subscription_details_task(
    send_to: str,
    transport: str = NotificationTransport.EMAIL.value,
    **kwargs,
) -> None:
    notification_transport = TRANSPORT_DISPATCHER[transport]
    transport_service = TransportService(notification_transport)
    transport_service.send_subscription_letter(
        send_to, subject=kwargs["subject"], content=kwargs["content"]
    )
