import abc
from typing import Type

from django.template import Context
from environ import environ

from notifications_api.apps.admin_emails.utils import render_html_text, render_subject
from notifications_api.emails.email_provider import EmailProvider, get_email_provider
from notifications_api.emails.schemas import (
    LetterWithAttachmentsSchema,
    WelcomeLetterSchema, SubscriptionInfoLetterSchema,
)

env = environ.Env()


class BaseTransport(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def send_welcome_letter(
        cls, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        pass

    @classmethod
    @abc.abstractmethod
    def send_email_with_attachments(
        cls, to: str, subject: str, body: str, attachments: str = None
    ):
        pass

    @classmethod
    @abc.abstractmethod
    def send_subscription_letter(
            cls, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        pass


class EmailTransport(BaseTransport):
    email_provider: Type[EmailProvider] = get_email_provider()

    @classmethod
    def send_welcome_letter(
        cls, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        subject, from_email, to = (
            subject or "Welcome Letter",
            env.str("MAILGUN_DOMAIN"),
            send_to,
        )
        text_content = (
            content or f"{username.capitalize()} привет! Рады, что выбрали нас 😍"
        )
        welcome_letter = WelcomeLetterSchema(
            from_email=from_email, to=to, subject=subject, content=text_content
        )
        cls.email_provider.send(welcome_letter)

    @classmethod
    def send_email_with_attachments(
        cls, to: str, subject: str, body: str, attachments: str = None
    ):
        ctx = Context()
        subject, from_email, to = (
            render_subject(ctx, subject),
            env.str("MAILGUN_DOMAIN"),
            to,
        )
        html_message = render_html_text(ctx, attachments)

        letter_with_attachments = LetterWithAttachmentsSchema(
            from_email=from_email,
            to=to,
            subject=subject,
            body=body,
            attachments=html_message,
        )
        cls.email_provider.send_with_attachments(letter_with_attachments)

    @classmethod
    def send_subscription_letter(
            cls, username: str, send_to: str, subject: str = "", content: str = ""
    ):
        subject, from_email, to = (
            subject or "Details about Subscription",
            env.str("MAILGUN_DOMAIN"),
            send_to,
        )
        text_content = (
                content or f"{username.capitalize()} привет! Вы успешно оплатили подписку 💸"
        )
        subscription_info_letter = SubscriptionInfoLetterSchema(
            from_email=from_email, to=to, subject=subject, content=text_content
        )
        cls.email_provider.send(subscription_info_letter)
