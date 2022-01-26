from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES["default"].update(NAME="billing", USER="billing", PASSWORD="password")

