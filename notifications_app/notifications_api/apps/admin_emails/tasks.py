from celery import shared_task
from django.utils import timezone

from notifications_api.apps.admin_emails.models import EmailTemplate
from notifications_api.apps.task_scheduler.scheduler import Scheduler
from notifications_api.apps.users.models import User
from notifications_api.emails.constants import NotificationTransport
from notifications_api.emails.services.transport_service import TransportService


@shared_task
def send_bulk_emails_task(**kwargs):
    for user in User.objects.all():
        scheduler = Scheduler(
            send_bulk_emails,
            params={
                "user": user.username,
                "email": user.email,
                "template_id": kwargs["template_id"],
            },
        )
        scheduler.create_task(timezone.now())


@shared_task
def schedule_send_bulk_emails_task(**kwargs):
    for user in User.objects.all():
        scheduler = Scheduler(
            send_bulk_emails,
            params={
                "user": user.username,
                "email": user.email,
                "template_id": kwargs["template_id"],
            },
        )
        scheduler.create_task(kwargs["launched_at"])


@shared_task
def send_bulk_emails(**kwargs):
    try:
        template = EmailTemplate.objects.get(kwargs["template_id"])
    except EmailTemplate.DoesNotExist:
        raise ValueError(f"There is no such template_id `{kwargs['template_id']}`")

    transport_service = TransportService(NotificationTransport.EMAIL.value)
    transport_service.send_email_with_attachments(
        to=kwargs["email"],
        subject=template.subject,
        body="",
        attachments=template.email_html_text,
    )
