import os
from .base import *

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

DEBUG = True


ALLOWED_HOSTS = [
    "sns-lb-staging-19447035-3f19227be0e5.kr.lb.naverncp.com",  # Staging Load balancer
    "localhost",
]

CSRF_TRUSTED_ORIGINS = [
    "http://sns-lb-staging-19447035-3f19227be0e5.kr.lb.naverncp.com/",  # Staging Load balancer
]
