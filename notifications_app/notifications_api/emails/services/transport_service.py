from typing import Type, TypeVar

from notifications_api.emails.notification_transport import BaseTransport

Transport = TypeVar("Transport", bound=BaseTransport)


class TransportService:
    def __init__(self, transport: Type[Transport]):
        self.transport = transport

    def send_welcome_letter(
        self, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        """Sends welcome message using transport"""
        self.transport.send_welcome_letter(username, send_to, subject, content)

    def send_email_with_attachments(
        self, to: str, subject: str, body: str, attachments: str
    ):
        self.transport.send_email_with_attachments(to, subject, body, attachments)

    def send_subscription_letter(
        self, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        """Sends welcome message using transport"""
        self.transport.send_subscription_letter(username, send_to, subject, content)
