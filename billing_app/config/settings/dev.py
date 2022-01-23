from .base import *

DEBUG = True

DATABASES["default"].update(NAME="billing", USER="billing", PASSWORD="password")
