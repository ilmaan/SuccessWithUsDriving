#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'successdriving.settings')
django.setup()

from django.contrib.auth.models import User
from drivingschool.models import Student
from drivingschool.forms import RegistrationForm

def test_registration():
    print("Testing registration form...")
    
    # Test data
    form_data = {
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'testuser@example.com',
        'username': 'testuser123',
        'password': 'testpassword123',
        'phone': '1234567890',
        'address': '123 Test St',
        'permit_no': 'TEST123'
    }
    
    # Clean up any existing test user
    try:
        existing_user = User.objects.get(username='testuser123')
        existing_user.delete()
        print("Cleaned up existing test user")
    except User.DoesNotExist:
        pass
    
    # Test form validation
    form = RegistrationForm(data=form_data)
    if form.is_valid():
        print("Form is valid")
        try:
            user = form.save()
            print(f"User created successfully: {user.username}")
            
            # Check if Student object was created
            try:
                student = Student.objects.get(user=user)
                print(f"Student profile created: {student}")
                print("Registration test PASSED")
            except Student.DoesNotExist:
                print("ERROR: Student profile not created")
                
        except Exception as e:
            print(f"ERROR creating user: {e}")
    else:
        print("Form validation failed:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    
    # Clean up
    try:
        User.objects.get(username='testuser123').delete()
        print("Test user cleaned up")
    except User.DoesNotExist:
        pass

if __name__ == '__main__':
    test_registration()