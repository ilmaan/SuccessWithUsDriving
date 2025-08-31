# driving_school/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('lessons/', views.lessons, name='lessons'),
    path('pricing/', views.pricing, name='pricing'),
    path('dmv-test-help/', views.dmv_test_help, name='dmv_test_help'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('careers/', views.careers, name='careers'),

    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('plan-selection/', views.plan_selection, name='plan_selection'),

    # Student
    path('student/', views.student_portal, name='student_portal'),
    path('student/book/', views.book_lesson, name='book_lesson'),
    path('student/cancel/<int:appt_id>/', views.cancel_appointment, name='cancel_appointment'),

    # Payment
    path('select-plan/<str:plan_name>/', views.select_plan, name='select_plan'),
    path('checkout/<int:plan_id>/', views.checkout, name='checkout'),
    path('payment-success/', views.payment_success, name='payment_success'),

    # Instructor
    path('instructor/', views.instructor_portal, name='instructor_portal'),
    path('instructor/complete/<int:appt_id>/', views.mark_complete, name='mark_complete'),

    # Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin/instructors/', views.manage_instructors, name='manage_instructors'),
    # path('admin/applications/', views.manage_applications, name='manage_applications'),

    # API
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
]
