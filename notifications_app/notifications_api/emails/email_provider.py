import abc
from functools import lru_cache
from typing import TypeVar

from django.core.mail import EmailMultiAlternatives

from notifications_api.emails.schemas import (
    LetterWithAttachmentsSchema,
    WelcomeLetterSchema,
)


class BaseEmailProvider(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def send(schema: WelcomeLetterSchema):
        pass

    @staticmethod
    @abc.abstractmethod
    def send_with_attachments(schema: LetterWithAttachmentsSchema):
        pass


EmailProvider = TypeVar("EmailProvider", bound=BaseEmailProvider)


class MailgunEmailProvider(BaseEmailProvider):
    @staticmethod
    def send(schema: WelcomeLetterSchema):
        subject, from_email, to = (
            schema.subject,
            schema.from_email,
            schema.to,
        )
        text_content = schema.content
        msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        msg.send()

    @staticmethod
    def send_with_attachments(schema: LetterWithAttachmentsSchema):
        msg = EmailMultiAlternatives(
            subject=schema.subject,
            body=schema.body,
            from_email=schema.from_email,
            to=schema.to,
        )
        msg.attach_alternative(schema.attachments, "text/html")
        msg.send()


@lru_cache()
def get_email_provider() -> EmailProvider:
    return MailgunEmailProvider()
