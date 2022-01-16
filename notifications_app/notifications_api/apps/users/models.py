import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(models.Model):
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=250)
    date_joined = models.DateTimeField(default=timezone.now)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return self.email
