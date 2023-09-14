from typing import Any
from django.core.management import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Checking if the database is empty"

    def handle(self, *args, **options):
        if not User.objects.exists():
            self.stdout.write("empty")
        else:
            self.stdout.write("not empty")
