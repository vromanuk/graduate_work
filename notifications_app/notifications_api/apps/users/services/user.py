from django.contrib.auth.models import User as DjangoBaseUser
from django.db import transaction

from notifications_api.apps.users.models import User


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(username: str, email: str) -> User:
        return User.objects.create(username=username, email=email)

    @staticmethod
    @transaction.atomic
    def create_superuser(default: bool = True):
        if default:
            return DjangoBaseUser.objects.create_superuser(
                username="admin", password="admin"
            )
