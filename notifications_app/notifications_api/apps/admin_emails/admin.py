from django.contrib import admin

from notifications_api.apps.admin_emails.tasks import (
    schedule_send_bulk_emails_task,
    send_bulk_emails_task,
)

from .models import EmailTemplate


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "subject")
    actions = ["schedule_send_bulk_emails", "send_bulk_emails"]

    @admin.action(description="Отправить заготовленное письмо для всех юзеров")
    def send_bulk_emails(self, request, queryset):
        email_template = queryset.get()
        send_bulk_emails_task.delay(template_id=email_template.id)

    @admin.action(description="Отправить отложенное письмо для всех юзеров")
    def schedule_send_bulk_emails(self, request, queryset):
        email_template = queryset.get()
        schedule_send_bulk_emails_task.delay(
            template_id=email_template.id, launched_at=email_template.scheduled_at
        )
