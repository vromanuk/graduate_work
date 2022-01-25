from pydantic import BaseModel


class BaseSchema(BaseModel):
    from_email: str
    to: str
    subject: str


class WelcomeLetterSchema(BaseSchema):
    content: str


class SubscriptionInfoLetterSchema(BaseSchema):
    content: str


class LetterWithAttachmentsSchema(BaseSchema):
    attachments: str
    body: str
