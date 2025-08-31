# driving_school/views.py
# import stripe
import random
import string
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from .models import *
from .forms import *

# Twilio setup
twilio_client = Client(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)

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
    plans = LessonPlan.objects.all()
    return render(request, 'pricing.html', {'plans': plans})

def dmv_test_help(request):
    return render(request, 'dmv-test-help.html')

def about(request):
    instructors = Instructor.objects.all()
    reviews = Review.objects.select_related('student', 'instructor').order_by('-created_at')[:3]
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
            user = form.save()
            login(request, user)
            return redirect('plan_selection')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

@login_required
@user_passes_test(is_student)
def plan_selection(request):
    plans = LessonPlan.objects.all()
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        if plan_id:
            return redirect('checkout', plan_id=plan_id)
    
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

# ======================
# Student Portal
# ======================

@login_required
@user_passes_test(is_student)
def student_portal(request):
    student = request.user.student
    appointments = Appointment.objects.filter(student=student).order_by('-scheduled_time')
    completed = appointments.filter(status='Completed').count()
    progress = (completed / max(student.total_credits, 1)) * 100
    return render(request, 'student-portal.html', {
        'student': student,
        'appointments': appointments,
        'completed': completed,
        'total': student.total_credits,
        'progress': progress
    })

@login_required
@user_passes_test(is_student)
def book_lesson(request):
    student = request.user.student
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.student = student
            if appt.scheduled_time < timezone.now():
                messages.error(request, "Can't book in the past.")
                return redirect('book_lesson')
            if Appointment.objects.filter(instructor=appt.instructor, scheduled_time=appt.scheduled_time).exists():
                messages.error(request, "Instructor not available.")
                return redirect('book_lesson')
            appt.save()
            # SMS Reminder
            twilio_client.messages.create(
                body=f"Hi {student.user.first_name}, your lesson is on {appt.scheduled_time.strftime('%b %d, %I:%M %p')}. See you soon!",
                from_=settings.TWILIO_PHONE,
                to=f"+1{student.phone}"
            )
            messages.success(request, "Lesson booked!")
            return redirect('student_portal')
    else:
        form = AppointmentForm()
        form.fields['instructor'].queryset = Instructor.objects.filter(is_available=True)
    return render(request, 'book-lesson.html', {'form': form})

@login_required
@user_passes_test(is_student)
def cancel_appointment(request, appt_id):
    appt = get_object_or_404(Appointment, id=appt_id, student=request.user.student)
    now = timezone.now()
    hours_diff = (appt.scheduled_time - now).total_seconds() / 3600
    if hours_diff < 24:
        refund = appt.credits_used // 2
        request.user.student.total_credits -= refund
        request.user.student.save()
        messages.warning(request, f"50% credit fee applied. {refund} credits deducted.")
    appt.status = 'Cancelled'
    appt.save()
    messages.success(request, "Cancelled.")
    return redirect('student_portal')

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
        q = request.POST.get('question', '').lower()
        reply = "I'm not sure. Please contact support@successwithus.com."
        faq = {
            'price': "Our packages start at $160 for 2 hours. Visit Pricing for details.",
            'schedule': "You can book lessons in your student portal after logging in.",
            'dmv': "We offer DMV test coaching, route practice, and paperwork help!",
            'cancel': "Cancel 24+ hours in advance for no charge. Within 24 hours, 50% credit fee applies.",
            'gift': "Ask us about gift cards for new drivers!",
            'referral': "Refer a friend and get 1 free lesson when they sign up!"
        }
        for key, ans in faq.items():
            if key in q:
                reply = ans
                break
        return JsonResponse({'reply': reply})
    return JsonResponse({'error': 'Only POST'}, status=400)
