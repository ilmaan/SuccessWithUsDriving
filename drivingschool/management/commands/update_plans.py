from django.core.management.base import BaseCommand
from drivingschool.models import LessonPlan, PlanFeature

class Command(BaseCommand):
    help = 'Update lesson plans with new package details'

    def handle(self, *args, **options):
        # Clear existing plans and features
        LessonPlan.objects.all().delete()
        
        # Create new plans based on the updated package schedule
        plans_data = [
            {
                'name': 'Quick Start',
                'hours': 2,
                'price': 160.00,
                'is_popular': False,
                'includes_test': False,
                'features': ['Core maneuvers', 'Expressway practice', 'Pickup/drop-off service']
            },
            {
                'name': 'Momentum Drive',
                'hours': 4,
                'price': 300.00,
                'is_popular': False,
                'includes_test': False,
                'features': ['Foundational skills', 'Advanced techniques', 'Pickup/drop-off service']
            },
            {
                'name': 'Confidence Cruise',
                'hours': 6,
                'price': 420.00,
                'is_popular': True,
                'includes_test': False,
                'features': ['Freeway driving', 'Parking mastery', 'Full support', 'Confidence building']
            },
            {
                'name': 'Master the Road',
                'hours': 8,
                'price': 560.00,
                'is_popular': False,
                'includes_test': False,
                'features': ['Deep training', 'Full skill set coverage', 'Advanced techniques']
            },
            {
                'name': 'Driven to Succeed',
                'hours': 10,
                'price': 650.00,
                'is_popular': False,
                'includes_test': False,
                'features': ['Comprehensive training', 'Lifelong habits development', 'Complete skill mastery']
            },
            {
                'name': 'Test Day Champion',
                'hours': 1,
                'price': 280.00,
                'is_popular': False,
                'includes_test': True,
                'features': ['DMV preparation', 'Car use for test', 'Pickup within 15 miles']
            }
        ]
        
        for plan_data in plans_data:
            features = plan_data.pop('features')
            plan = LessonPlan.objects.create(**plan_data)
            
            # Create features for this plan
            for i, feature_text in enumerate(features):
                PlanFeature.objects.create(
                    plan=plan,
                    feature_text=feature_text,
                    order=i + 1
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created plan: {plan.name} - ${plan.price} with {len(features)} features')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully updated all lesson plans!')
        )