import uuid

from django.db import models


class Task(models.Model):
    class State(models.IntegerChoices):
        PENDING = 1
        RUNNING = 2
        FAILED = 3
        FINISHED = 4
        CANCELED = 5

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    handle = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    launched_at = models.DateTimeField(db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    params = models.JSONField("task_params", null=True, blank=True)
    state = models.IntegerField(choices=State.choices, default=State.PENDING)
