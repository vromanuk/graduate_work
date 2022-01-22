from .base import *

DEBUG = True

DATABASES["default"].update(NAME="billing", USER="developer", PASSWORD="password")
