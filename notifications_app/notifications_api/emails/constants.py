import enum

from notifications_api.emails.notification_transport import EmailTransport


@enum.unique
class NotificationTransport(enum.Enum):
    EMAIL = "email"


TRANSPORT_DISPATCHER = {NotificationTransport.EMAIL.value: EmailTransport}
