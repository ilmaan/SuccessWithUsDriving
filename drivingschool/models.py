# driving_school/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    permit_no = models.CharField(max_length=50, blank=True)
    license_status = models.CharField(max_length=50, default="Learner's Permit")
    total_credits = models.IntegerField(default=0)
    documents = models.FileField(upload_to='students/docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    bio = models.TextField()
    experience_years = models.IntegerField(default=2)
    rating = models.FloatField(default=5.0)
    is_available = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='instructors/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class LessonPlan(models.Model):
    name = models.CharField(max_length=100)
    hours = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_popular = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No-show', 'No-show'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    plan = models.ForeignKey(LessonPlan, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    credits_used = models.IntegerField(default=1)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student} - {self.scheduled_time}"

class Review(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.student} for {self.instructor}"

class JobApplication(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    cv = models.FileField(upload_to='careers/')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class GiftCard(models.Model):
    code = models.CharField(max_length=20, unique=True)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    is_used = models.BooleanField(default=False)
    used_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Gift Card ${self.value} ({self.code})"

class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referrals_given')
    referred_email = models.EmailField()
    is_converted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.referrer} referred {self.referred_email}"