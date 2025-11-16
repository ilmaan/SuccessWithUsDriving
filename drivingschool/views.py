# driving_school/views.py
# import stripe
import json
import random
import string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
# from twilio.rest import Client
from .models import *
from .forms import *

# Twilio setup
# twilio_client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

# Stripe setup
# stripe.api_key = settings.STRIPE_SECRET_KEY

def is_student(user):
    return hasattr(user, 'student')

def is_instructor(user):
    return hasattr(user, 'instructor')

def is_admin(user):
    return user.is_superuser

# ======================
# Public Pages
# ======================

def home(request):
    plans = LessonPlan.objects.all()
    total_students = Student.objects.count()
    return render(request, 'index.html', {
        'plans': plans,
        'total_students': total_students,
        'pass_rate': '98%'
    })

def lessons(request):
    return render(request, 'lessons.html')

def pricing(request):
    standard_plans = LessonPlan.objects.filter(package_type='standard', is_active=True).order_by('display_order', 'name')
    specialized_plans = LessonPlan.objects.filter(package_type='specialized', is_active=True).order_by('display_order', 'name')
    
    context = {
        'standard_plans': standard_plans,
        'specialized_plans': specialized_plans,
    }
    return render(request, 'pricing.html', context)

def dmv_test_help(request):
    return render(request, 'dmv-test-help.html')

def about(request):
    instructors = Instructor.objects.all()
    reviews = Review.objects.order_by('-created_at')[:3]
    return render(request, 'about.html', {'instructors': instructors, 'reviews': reviews})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        send_mail(
            subject=f"Contact from {name}",
            message=message,
            recipient_list=[settings.ADMIN_EMAIL],
            from_email=email
        )
        messages.success(request, "Message sent!")
        return redirect('contact')
    return render(request, 'contact.html')

def careers(request):
    try:
        if request.method == 'POST':
            form = JobApplicationForm(request.POST, request.FILES)
            if form.is_valid():
                app = form.save()
                # # Send SMS to admin
                # twilio_client.messages.create(
                #     body=f"New job application from {app.first_name} {app.last_name}",
                #     from_=settings.TWILIO_PHONE,
                #     to=settings.ADMIN_PHONE
                # )
                messages.success(request, "Application submitted!")
                print(f"Application submitted: {app}")
                return redirect('careers')
    except Exception as e:
        print("ERROR: ", e)
        messages.error(request, f"Error: {e}")
    else:
        form = JobApplicationForm()
    return render(request, 'careers.html', {'form': form}) 

# ======================
# Authentication
# ======================

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                # Check if there's a next parameter
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                # Redirect students to student portal after registration
                return redirect('student_portal')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
def plan_selection(request):
    # Ensure user has a Student object
    if not hasattr(request.user, 'student'):
        try:
            Student.objects.create(user=request.user)
        except Exception as e:
            messages.error(request, 'Unable to create student profile. Please contact support.')
            return redirect('home')
    plans = LessonPlan.objects.all()
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        if plan_id:
            return redirect('purchase_plan', plan_id=plan_id)
    
    selected_plan_name = request.session.get('selected_plan_name', None)
    
    # Clear the session variable after using it
    if 'selected_plan_name' in request.session:
        del request.session['selected_plan_name']
    
    return render(request, 'plan_selection.html', {
        'plans': plans,
        'selected_plan_name': selected_plan_name
    })

def login_view(request):
    if request.method == 'POST':
        username_or_email = request.POST['username']
        password = request.POST['password']
        
        # Try to authenticate with username first
        user = authenticate(request, username=username_or_email, password=password)
        
        # If that fails, try to find user by email and authenticate
        if not user:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        
        if user:
            login(request, user)
            # Handle remember me functionality
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)  # Session expires when browser closes
            
            if is_student(user): return redirect('student_portal')
            if is_instructor(user): return redirect('instructor_portal')
            if is_admin(user): return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid email/username or password.")
    return render(request, 'login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

# ======================
# Error Handlers
# ======================

def redirect_to_about(request, exception=None):
    """Redirect any 404 page to the About page."""
    return redirect('about')

# ======================
# Student Portal
# ======================

@login_required
@user_passes_test(is_student)
def student_portal(request):
    student = request.user.student
    appointments = Appointment.objects.filter(student=student).order_by('-scheduled_time')
    completed = appointments.filter(status='Completed').count()
    progress = (completed / max(student.total_credits, 1)) * 100 if student.total_credits > 0 else 0
    
    # Get available plans for purchase
    plans = LessonPlan.objects.all()
    
    # Get student's plan purchases
    plan_purchases = StudentPlanPurchase.objects.filter(student=student, payment_status='completed')
    
    # Get cart items count
    try:
        cart = Cart.objects.get(student=student)
        cart_items_count = CartItem.objects.filter(cart=cart).count()
    except Cart.DoesNotExist:
        cart_items_count = 0
    
    # Get purchased plans
    purchased_plans = StudentPlanPurchase.objects.filter(
        student=student,
        payment_status='completed'
    ).select_related('plan').order_by('-purchase_date')
    
    # Get available instructors for reschedule modal
    instructors = Instructor.objects.filter(is_available=True)
    
    return render(request, 'student-portal.html', {
        'student': student,
        'appointments': appointments,
        'completed': completed,
        'total': student.total_credits,
        'progress': progress,
        'plans': plans,
        'plan_purchases': plan_purchases,
        'available_credits': student.available_credits,
        'cart_items_count': cart_items_count,
        'purchased_plans': purchased_plans,
        'instructors': instructors
    })

@login_required
@user_passes_test(is_student)
def add_to_cart(request, plan_id):
    """Add a plan to the student's cart"""
    plan = get_object_or_404(LessonPlan, id=plan_id)
    student = request.user.student
    
    # Get or create cart for the student
    cart, created = Cart.objects.get_or_create(student=student)
    
    # Try to add the plan to cart (will fail if already exists due to unique constraint)
    try:
        CartItem.objects.create(cart=cart, plan=plan)
        messages.success(request, f'{plan.name} has been added to your cart!')
    except:
        messages.info(request, f'{plan.name} is already in your cart.')
    
    # Redirect to checkout instead of student portal
    return redirect('checkout_cart')

@login_required
@user_passes_test(is_student)
def booking_page(request):
    """Display the calendar-based booking interface"""
    student = request.user.student
    if student.available_credits < 1:
        messages.error(request, 'You need to purchase a plan before booking a lesson.')
        return redirect('plan_selection')
    instructors = Instructor.objects.filter(is_available=True)

    # Determine eligible lesson type from purchased plans
    purchases = StudentPlanPurchase.objects.filter(
        student=student,
        payment_status='completed'
    ).select_related('plan').order_by('-purchase_date')

    if purchases.filter(plan__includes_test=True).exists():
        eligible_lesson_type = 'test_prep'
        eligible_lesson_type_label = 'Test Preparation'
    else:
        eligible_lesson_type = 'beginner'
        eligible_lesson_type_label = 'Beginner Lesson'

    return render(request, 'booking.html', {
        'instructors': instructors,
        'eligible_lesson_type': eligible_lesson_type,
        'eligible_lesson_type_label': eligible_lesson_type_label,
    })

@login_required
@user_passes_test(is_student)
def book_lesson(request):
    student = request.user.student
    if request.method == 'POST':
        # Require at least 1 available credit to book
        if student.available_credits < 1:
            messages.error(request, 'You have no available credits. Please purchase a plan first.')
            return redirect('plan_selection')
        
        # Handle calendar-based booking form
        selected_date = request.POST.get('selected_date')
        selected_time = request.POST.get('selected_time')
        selected_instructor_id = request.POST.get('selected_instructor')
        special_requirements = request.POST.get('special_requirements', '')
        
        if selected_date and selected_time and selected_instructor_id:
            try:
                # Parse date and time
                date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
                time_obj = datetime.strptime(selected_time, '%H:%M').time()
                scheduled_datetime = datetime.combine(date_obj, time_obj)
                scheduled_datetime = timezone.make_aware(scheduled_datetime)
                
                # Get instructor
                instructor = get_object_or_404(Instructor, id=selected_instructor_id, is_available=True)
                
                # Validate booking
                if scheduled_datetime < timezone.now():
                    messages.error(request, "Can't book in the past.")
                    return redirect('booking_page')
                    
                if Appointment.objects.filter(instructor=instructor, scheduled_time=scheduled_datetime).exists():
                    messages.error(request, "Instructor not available at this time.")
                    return redirect('booking_page')

                # Determine eligible lesson type and plan from purchases
                purchases = StudentPlanPurchase.objects.filter(
                    student=student,
                    payment_status='completed'
                ).select_related('plan').order_by('-purchase_date')

                test_purchase = purchases.filter(plan__includes_test=True).first()
                if test_purchase:
                    enforced_lesson_type = 'test_prep'
                    enforced_plan = test_purchase.plan
                else:
                    enforced_lesson_type = 'beginner'
                    enforced_plan = purchases.first().plan if purchases.exists() else None
                
                # Create appointment
                appointment = Appointment.objects.create(
                    student=student,
                    instructor=instructor,
                    scheduled_time=scheduled_datetime,
                    lesson_type=enforced_lesson_type,
                    special_requirements=special_requirements,
                    status='Scheduled',
                    credits_used=1,
                    plan=enforced_plan
                )
                
                # Deduct one credit on booking
                student.available_credits = max(0, student.available_credits - 1)
                student.save()
                
                messages.success(request, f"Lesson booked successfully for {scheduled_datetime.strftime('%B %d, %Y at %I:%M %p')}! 1 credit has been deducted.")
                return redirect('student_portal')
                
            except Exception as e:
                messages.error(request, f"Error booking lesson: {str(e)}")
                return redirect('booking_page')
        else:
            messages.error(request, "Please select date, time, and instructor.")
            return redirect('booking_page')
    else:
        # For GET requests, redirect to booking page
        return redirect('booking_page')

@login_required
@user_passes_test(is_student)
def cancel_appointment(request, appt_id=None):
    if request.method == 'POST':
        try:
            student = request.user.student
            
            # Get appointment_id from POST data or URL parameter
            appointment_id = request.POST.get('appointment_id') or appt_id
            if not appointment_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Appointment ID is required.'
                })
            
            appointment = get_object_or_404(Appointment, id=appointment_id, student=student)
            
            # Check if appointment can be cancelled
            if appointment.status == 'Completed':
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot cancel a completed appointment.'
                })
            
            if appointment.status == 'Cancelled':
                return JsonResponse({
                    'success': False,
                    'error': 'Appointment is already cancelled.'
                })
            
            # Check if cancellation is at least 24 hours before appointment
            time_until_appointment = appointment.scheduled_time - timezone.now()
            if time_until_appointment.total_seconds() < 24 * 3600:  # 24 hours
                return JsonResponse({
                    'success': False,
                    'error': 'Appointments can only be cancelled at least 24 hours in advance.'
                })
            
            # Cancel the appointment
            appointment.status = 'Cancelled'
            appointment.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Appointment cancelled successfully.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

@login_required
@user_passes_test(is_student)
def reschedule_appointment(request):
    if request.method == 'POST':
        try:
            student = request.user.student
            appointment_id = request.POST.get('appointment_id')
            new_date = request.POST.get('new_date')
            new_time = request.POST.get('new_time')
            instructor_id = request.POST.get('instructor_id')
            reason = request.POST.get('reason', '')
            
            # Validate required fields
            if not all([appointment_id, new_date, new_time, instructor_id]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required.'
                })
            
            # Get the appointment
            appointment = get_object_or_404(Appointment, id=appointment_id, student=student)
            
            # Check if appointment can be rescheduled
            if appointment.status == 'Completed':
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot reschedule a completed appointment.'
                })
            
            if appointment.status == 'Cancelled':
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot reschedule a cancelled appointment.'
                })
            
            # Check if rescheduling is at least 24 hours before current appointment
            time_until_appointment = appointment.scheduled_time - timezone.now()
            if time_until_appointment.total_seconds() < 24 * 3600:  # 24 hours
                return JsonResponse({
                    'success': False,
                    'error': 'Appointments can only be rescheduled at least 24 hours in advance.'
                })
            
            # Parse new date and time
            try:
                date_obj = datetime.strptime(new_date, '%Y-%m-%d').date()
                time_obj = datetime.strptime(new_time, '%H:%M').time()
                new_scheduled_datetime = datetime.combine(date_obj, time_obj)
                new_scheduled_datetime = timezone.make_aware(new_scheduled_datetime)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid date or time format.'
                })
            
            # Validate new appointment time is in the future
            if new_scheduled_datetime <= timezone.now():
                return JsonResponse({
                    'success': False,
                    'error': 'Cannot schedule appointment in the past.'
                })
            
            # Get instructor
            try:
                instructor = Instructor.objects.get(id=instructor_id, is_available=True)
            except Instructor.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Selected instructor is not available.'
                })
            
            # Check if new time slot is available
            existing_appointment = Appointment.objects.filter(
                instructor=instructor,
                scheduled_time=new_scheduled_datetime
            ).exclude(id=appointment_id).exists()
            
            if existing_appointment:
                return JsonResponse({
                    'success': False,
                    'error': 'Selected time slot is not available.'
                })
            
            # Update the appointment
            appointment.scheduled_time = new_scheduled_datetime
            appointment.instructor = instructor
            if reason:
                appointment.notes = f"Rescheduled: {reason}" + (f" | Previous notes: {appointment.notes}" if appointment.notes else "")
            appointment.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Appointment rescheduled successfully for {new_scheduled_datetime.strftime("%B %d, %Y at %I:%M %p")}.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method.'
    })

# ======================
# Payment
# ======================

@login_required
def select_plan(request, plan_name):
    """Handle plan selection by name and redirect to plan selection page"""
    # Map plan names to LessonPlan names for integration with our plan selection system
    plan_mapping = {
        'starter': 'Starter Package',
        'standard': 'Standard Package', 
        'premium': 'Premium Package',
        'test-prep': 'Test Prep Package',
        'refresher': 'Refresher Package',
        'defensive': 'Defensive Driving'
    }
    
    plan_display_name = plan_mapping.get(plan_name, plan_name.title())
    
    # Store the selected plan name in session for pre-selection in plan_selection view
    request.session['selected_plan_name'] = plan_display_name
    
    # Redirect to our plan selection page where user can confirm and proceed to checkout
    return redirect('plan_selection')

@login_required
@user_passes_test(is_student)
def add_to_cart(request, plan_id):
    """Add a plan to the student's cart"""
    plan = get_object_or_404(LessonPlan, id=plan_id)
    student = request.user.student
    
    # Get or create cart for the student
    cart, created = Cart.objects.get_or_create(student=student)
    
    # Try to add the plan to cart (will fail if already exists due to unique constraint)
    try:
        CartItem.objects.create(cart=cart, plan=plan)
        messages.success(request, f'{plan.name} has been added to your cart!')
    except:
        messages.info(request, f'{plan.name} is already in your cart.')
    
    return redirect('checkout_cart')

@login_required
@user_passes_test(is_student)
def add_to_cart_and_checkout(request, plan_name):
    """Add a plan to cart by name and redirect to checkout"""
    # Map plan names to match the database
    plan_name_mapping = {
        'quick-start': 'Quick Start',
        'momentum-drive': 'Momentum Drive', 
        'confidence-cruise': 'Confidence Cruise',
        'master-the-road': 'Master the Road',
        'driven-to-succeed': 'Driven to Succeed',
        'test-day-champion': 'Test Day Champion'
    }
    
    actual_plan_name = plan_name_mapping.get(plan_name, plan_name.replace('-', ' ').title())
    plan = get_object_or_404(LessonPlan, name=actual_plan_name)
    student = request.user.student
    
    # Get or create cart for the student
    cart, created = Cart.objects.get_or_create(student=student)
    
    # Try to add the plan to cart (will fail if already exists due to unique constraint)
    try:
        CartItem.objects.create(cart=cart, plan=plan)
        messages.success(request, f'{plan.name} has been added to your cart!')
    except:
        messages.info(request, f'{plan.name} is already in your cart.')
    
    # Redirect to checkout instead of student portal
    return redirect('checkout_cart')

@login_required
@user_passes_test(is_student)
def view_cart(request):
    """Display the student's cart"""
    student = request.user.student
    
    try:
        cart = Cart.objects.get(student=student)
        cart_items = CartItem.objects.filter(cart=cart).select_related('plan')
    except Cart.DoesNotExist:
        cart = None
        cart_items = []
    
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price() if cart else 0,
        'total_credits': cart.get_total_credits() if cart else 0
    })

@login_required
@user_passes_test(is_student)
def remove_from_cart(request, item_id):
    """Remove an item from the cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__student=request.user.student)
    plan_name = cart_item.plan.name
    cart_item.delete()
    messages.success(request, f'{plan_name} has been removed from your cart.')
    return redirect('view_cart')

@login_required
@user_passes_test(is_student)
def checkout_cart(request):
    """Process cart checkout"""
    student = request.user.student
    
    try:
        cart = Cart.objects.get(student=student)
        cart_items = CartItem.objects.filter(cart=cart).select_related('plan')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('view_cart')
        
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('student_portal')
    
    return render(request, 'checkout_cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
        'total_credits': cart.get_total_credits()
    })

def checkout(request, plan_id):
    plan = get_object_or_404(LessonPlan, id=plan_id)
    if request.method == 'POST':
        try:
            # session = stripe.checkout.Session.create(
            #     payment_method_types=['card'],
            #     line_items=[{
            #         'price_data': {
            #             'currency': 'usd',
            #             'product_data': {'name': plan.name},
            #             'unit_amount': int(plan.price * 100),
            #         },
            #         'quantity': 1,
            #     }],
            #     mode='payment',
            #     success_url=request.build_absolute_uri('/payment-success/') + f'?plan_id={plan.id}',
            #     cancel_url=request.build_absolute_uri('/pricing/'),
            # )
            # return redirect(session.url, code=303)
            pass
        except Exception as e:
            messages.error(request, str(e))
    return render(request, 'checkout.html', {'plan': plan})

def payment_success(request):
    plan_id = request.GET.get('plan_id')
    plan = get_object_or_404(LessonPlan, id=plan_id)
    student = request.user.student
    student.total_credits += plan.hours
    student.save()
    messages.success(request, f"{plan.hours} credits added!")
    return redirect('student_portal')

@login_required
@user_passes_test(is_student)
def process_cart_payment(request):
    """Process payment for all items in the cart"""
    if request.method != 'POST':
        return redirect('view_cart')
    
    student = request.user.student
    
    try:
        cart = Cart.objects.get(student=student)
        cart_items = CartItem.objects.filter(cart=cart).select_related('plan')
        
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('view_cart')
        
        # Process each item in the cart
        total_credits = 0
        purchased_plans = []
        
        for item in cart_items:
            # Create purchase record
            purchase = StudentPlanPurchase.objects.create(
                student=student,
                plan=item.plan,
                credits_granted=item.plan.hours,
                payment_status='completed',
                payment_id=f"PAY_{random.randint(100000, 999999)}"
            )
            
            total_credits += item.plan.hours
            purchased_plans.append(item.plan.name)
        
        # Update student credits
        student.available_credits += total_credits
        student.total_credits += total_credits
        student.save()
        
        # Clear the cart
        cart_items.delete()
        
        # Success message
        plan_names = ', '.join(purchased_plans)
        messages.success(request, f'Payment successful! You have purchased: {plan_names}. {total_credits} credits have been added to your account.')
        
        return redirect('student_portal')
        
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('student_portal')

@login_required
@user_passes_test(is_student)
def purchase_plan(request, plan_id):
    """Direct purchase of a plan - creates purchase record and redirects to payment"""
    student = request.user.student
    plan = get_object_or_404(LessonPlan, id=plan_id)
    
    # Create purchase record
    purchase = StudentPlanPurchase.objects.create(
        student=student,
        plan=plan,
        credits_granted=plan.hours,
        payment_status='pending'
    )
    
    # Redirect to payment page
    return redirect('payment_page', purchase_id=purchase.id)

@login_required
@user_passes_test(is_student)
def payment_page(request, purchase_id):
    """Dummy payment page that bypasses actual payment processing"""
    purchase = get_object_or_404(StudentPlanPurchase, id=purchase_id, student=request.user.student)
    
    if request.method == 'POST':
        # Simulate payment processing
        purchase.payment_status = 'completed'
        purchase.payment_id = f"PAY_{random.randint(100000, 999999)}"
        purchase.save()
        
        # Add credits to student account
        student = purchase.student
        student.available_credits += purchase.credits_granted
        student.total_credits += purchase.credits_granted
        student.save()
        
        messages.success(request, f'Payment successful! {purchase.credits_granted} credits have been added to your account.')
        return redirect('student_portal')
    
    return render(request, 'payment_page.html', {
        'purchase': purchase,
        'plan': purchase.plan
    })

# ======================
# Instructor Portal
# ======================

@login_required
@user_passes_test(is_instructor)
def instructor_portal(request):
    instructor = request.user.instructor
    appointments = Appointment.objects.filter(instructor=instructor).order_by('scheduled_time')
    return render(request, 'instructor-portal.html', {
        'instructor': instructor,
        'appointments': appointments
    })

@login_required
@user_passes_test(is_instructor)
def mark_complete(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, instructor=request.user.instructor)
    if appt.status == 'Scheduled':
        appt.status = 'Completed'
        appt.save()
        # Credit already deducted on booking
        messages.success(request, "Marked complete.")
    return redirect('instructor_portal')

# ======================
# Admin Dashboard
# ======================

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html', {
        'students': Student.objects.count(),
        'instructors': Instructor.objects.count(),
        'appointments': Appointment.objects.count(),
        'revenue': sum(a.plan.price for a in Appointment.objects.filter(status='Completed') if a.plan),
        'applications': JobApplication.objects.count(),
    })

# ======================
# AI Chatbot
# ======================

# ======================
# Dashboard Redirect
# ======================

@login_required
def dashboard(request):
    """Redirect users to their appropriate dashboard based on role"""
    if is_student(request.user):
        return redirect('student_portal')
    elif is_instructor(request.user):
        return redirect('instructor_portal')
    elif is_admin(request.user):
        return redirect('admin_dashboard')
    else:
        messages.error(request, "No dashboard available for your account type.")
        return redirect('home')

# ======================
# AI Chatbot
# ======================

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            # Simple chatbot responses
            responses = {
                'hello': 'Hi! How can I help you with your driving lessons today?',
                'pricing': 'Our lesson plans start from $299. Visit our pricing page for details!',
                'book': 'You can book a lesson from your student dashboard.',
                'contact': 'You can reach us at (555) 123-4567 or email info@successdriving.com'
            }
            
            response = responses.get(message.lower(), 'I\'m here to help! Ask me about pricing, booking, or contact information.')
            
            return JsonResponse({
                'response': response
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def get_available_slots(request):
    """API endpoint to get available time slots for a specific instructor and date"""
    if request.method == 'GET':
        try:
            instructor_id = request.GET.get('instructor_id')
            date_str = request.GET.get('date')
            
            if not instructor_id or not date_str:
                return JsonResponse({'error': 'instructor_id and date are required'}, status=400)
            
            # Parse the date
            try:
                selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
            
            # Get instructor
            try:
                instructor = Instructor.objects.get(id=instructor_id, is_available=True)
            except Instructor.DoesNotExist:
                return JsonResponse({'error': 'Instructor not found or not available'}, status=404)
            
            # Define all possible time slots (9 AM to 5 PM)
            all_slots = [
                '09:00', '10:00', '11:00', '12:00', 
                '13:00', '14:00', '15:00', '16:00', '17:00'
            ]
            
            # Get booked appointments for this instructor on this date
            booked_appointments = Appointment.objects.filter(
                instructor=instructor,
                scheduled_time__date=selected_date,
                status__in=['Scheduled']  # Only consider scheduled appointments
            )
            
            # Extract booked time slots
            booked_times = []
            for appointment in booked_appointments:
                booked_times.append(appointment.scheduled_time.strftime('%H:%M'))
            
            # Filter out booked slots
            available_slots = [slot for slot in all_slots if slot not in booked_times]
            
            # Don't show past time slots for today
            if selected_date == timezone.now().date():
                current_time = timezone.now().time()
                available_slots = [
                    slot for slot in available_slots 
                    if datetime.strptime(slot, '%H:%M').time() > current_time
                ]
            
            return JsonResponse({
                'available_slots': available_slots,
                'booked_slots': booked_times,
                'instructor_name': instructor.user.get_full_name(),
                'date': date_str
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
