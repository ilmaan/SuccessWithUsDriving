from django.core.management.base import BaseCommand
from drivingschool.models import LessonPlan

class Command(BaseCommand):
    help = 'Update lesson plans with new package details'

    def handle(self, *args, **options):
        # Clear existing plans
        LessonPlan.objects.all().delete()
        
        # Create new plans based on the updated package schedule
        plans_data = [
            {
                'name': 'Quick Start',
                'hours': 2,
                'price': 160.00,
                'is_popular': False,
                'description': 'Core maneuvers, expressway practice, pickup/drop-off'
            },
            {
                'name': 'Momentum Drive',
                'hours': 4,
                'price': 300.00,
                'is_popular': False,
                'description': 'Foundational skills + advanced techniques'
            },
            {
                'name': 'Confidence Cruise',
                'hours': 6,
                'price': 420.00,
                'is_popular': True,
                'description': 'Freeway driving, parking mastery, full support'
            },
            {
                'name': 'Master the Road',
                'hours': 8,
                'price': 560.00,
                'is_popular': False,
                'description': 'Deep training, full skill set coverage'
            },
            {
                'name': 'Driven to Succeed',
                'hours': 10,
                'price': 650.00,
                'is_popular': False,
                'description': 'Comprehensive training, lifelong habits'
            },
            {
                'name': 'Test Day Champion',
                'hours': 1,
                'price': 280.00,
                'is_popular': False,
                'description': 'DMV prep, car use, pickup within 15 miles'
            }
        ]
        
        for plan_data in plans_data:
            plan = LessonPlan.objects.create(**plan_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created plan: {plan.name} - ${plan.price}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated all lesson plans!')
        )