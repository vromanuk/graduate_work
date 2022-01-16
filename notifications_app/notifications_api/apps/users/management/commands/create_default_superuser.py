from django.core.management.base import BaseCommand

from notifications_api.apps.users.services.user import UserService


class Command(BaseCommand):
    help = "Creates default superuser: `login`: admin, `password`: admin"

    def handle(self, *args, **kwargs):
        UserService.create_superuser()
