from celery import shared_task
from django.utils import timezone

from notifications_api.apps.task_scheduler.models import Task
from notifications_api.apps.task_scheduler.utils import fully_qualified_name_to_obj


@shared_task
def execute_scheduled_tasks():
    tasks = Task.objects.filter(
        launched_at__lte=timezone.now(), state=Task.State.PENDING
    )
    for task in tasks:
        task.state = Task.State.RUNNING
        task.save()
        try:
            func = fully_qualified_name_to_obj(task.handle)
            func.apply_async(
                kwargs=task.params, link=sync_running_task.s(str(task.uuid))
            )
        except Exception:
            task.state = Task.State.FAILED
            task.save()


@shared_task
def sync_running_task(error, task_uuid):
    if error:
        state = Task.State.FAILED
    else:
        state = Task.State.FINISHED
    Task.objects.filter(uuid=task_uuid).update(state=state, finished_at=timezone.now())
