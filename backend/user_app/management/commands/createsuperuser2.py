from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
User = get_user_model()
class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            email = input("Email: ")
            password = input("Password: ")
            User.objects.create_superuser(email=email, password=password)
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")