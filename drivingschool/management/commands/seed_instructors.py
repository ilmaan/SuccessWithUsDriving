from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from drivingschool.models import Instructor
import random

class Command(BaseCommand):
    def handle(self, *args, **options):
        data = [
            {
                'first_name': 'Mohommad',
                'last_name': '',
                'username': 'mohommad',
                'email': 'mohommad@example.com',
            },
            {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'john_doe',
                'email': 'john.doe@example.com',
            },
        ]

        for item in data:
            user, created = User.objects.get_or_create(
                username=item['username'],
                defaults={
                    'first_name': item['first_name'],
                    'last_name': item['last_name'],
                    'email': item['email'],
                }
            )
            if created:
                user.set_password('Test1234!')
                user.save()

            instr, _ = Instructor.objects.get_or_create(
                user=user,
                defaults={
                    'phone': f"(408) 555-{random.randint(1000,9999)}",
                    'bio': 'Experienced driving instructor focused on safe, confident driving.',
                    'experience_years': random.choice([2, 3, 4, 5, 7, 10]),
                    'rating': round(random.uniform(4.5, 5.0), 1),
                    'is_available': True,
                }
            )
        self.stdout.write(self.style.SUCCESS('Seeded instructor accounts.'))