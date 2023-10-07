import os
from .base import *

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = False


ALLOWED_HOSTS += []

CSRF_TRUSTED_ORIGINS += []
