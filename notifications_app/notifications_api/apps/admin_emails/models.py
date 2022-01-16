from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailTemplate(models.Model):
    class Meta:
        verbose_name = "Email template"
        verbose_name_plural = "Email templates"

    name = models.CharField(verbose_name=_("template name"), max_length=254)

    description = models.TextField(verbose_name=_("description"), blank=True)

    subject = models.CharField(
        verbose_name=_("template subject"),
        max_length=254,
        blank=False,
    )

    email_html_text = models.TextField(
        verbose_name="HTML",
        blank=True,
    )

    scheduled_at = models.DateTimeField(
        _("schedule email mailing"), blank=True, null=True, db_index=True
    )
