#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'successdriving.settings')
django.setup()

from drivingschool.models import LessonPlan
from decimal import Decimal

def add_original_prices():
    """Add original prices to existing lesson plans to demonstrate discount functionality"""
    
    # Get all lesson plans
    plans = LessonPlan.objects.all()
    
    for plan in plans:
        # Add original price that's higher than current price to show discount
        if plan.price:
            # Set original price to be 20-30% higher than current price
            original_price = plan.price * Decimal('1.25')  # 25% higher
            plan.original_price = original_price
            plan.save()
            print(f"Updated {plan.name}: Current Price £{plan.price}, Original Price £{original_price}")
        else:
            print(f"Skipped {plan.name}: No current price set")
    
    print(f"\nUpdated {plans.count()} lesson plans with original prices")

if __name__ == '__main__':
    add_original_prices()