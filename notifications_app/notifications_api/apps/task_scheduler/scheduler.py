from django.utils import timezone

from notifications_api.apps.task_scheduler.models import Task
from notifications_api.apps.task_scheduler.utils import object_to_fully_qualified_name


class Scheduler:
    def __init__(self, handle=None, params=None):
        if handle:
            self.handle = object_to_fully_qualified_name(handle)
        if not params:
            self.params = dict()
        else:
            self.params = params

    def create_task(self, launched_at):
        return Task.objects.create(
            handle=self.handle, params=self.params, launched_at=launched_at
        )

    def cancel_task(self):
        return Task.objects.filter(handle=self.handle, state=Task.State.PENDING).update(
            handle=self.handle, state=Task.State.CANCELED, finished_at=timezone.now()
        )
