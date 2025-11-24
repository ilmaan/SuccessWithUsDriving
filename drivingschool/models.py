# driving_school/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    permit_no = models.CharField(max_length=50, blank=True)
    license_status = models.CharField(max_length=50, default="Learner's Permit")
    total_credits = models.IntegerField(default=0)
    available_credits = models.IntegerField(default=0)
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

    @property
    def experience(self):
        return self.experience_years

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class LessonPlan(models.Model):
    PACKAGE_TYPE_CHOICES = [
        ('standard', 'Standard Package'),
        ('specialized', 'Specialized Package'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, help_text="URL-friendly name for the plan", blank=True)
    description = models.TextField(help_text="Brief description of the package", default="Professional driving instruction package")
    hours = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    original_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Original price before discount")
    is_popular = models.BooleanField(default=False)
    includes_test = models.BooleanField(default=False)
    package_type = models.CharField(max_length=20, choices=PACKAGE_TYPE_CHOICES, default='standard')
    display_order = models.PositiveIntegerField(default=0, help_text="Order in which to display the plan")
    is_active = models.BooleanField(default=True, help_text="Whether this plan is currently available")
    
    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name
    
    @property
    def has_discount(self):
        return self.original_price and self.original_price > self.price

class PlanFeature(models.Model):
    plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE, related_name='features')
    feature_text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.plan.name} - {self.feature_text}"

class Cart(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.student.user.get_full_name()}"
    
    def get_total_price(self):
        return sum(item.plan.price for item in self.cartitem_set.all())
    
    def get_total_credits(self):
        return sum(item.plan.hours for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'plan')  # Prevent duplicate plans in cart
    
    def __str__(self):
        return f"{self.cart.student.user.get_full_name()} - {self.plan.name}"

class StudentPlanPurchase(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    plan = models.ForeignKey(LessonPlan, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    credits_granted = models.IntegerField()
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=100, blank=True)  # For future payment integration
    
    def __str__(self):
        return f"{self.student} - {self.plan.name} ({self.payment_status})"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('No-show', 'No-show'),
    ]
    
    LESSON_TYPE_CHOICES = [
        ('beginner', 'Beginner Lesson'),
        ('intermediate', 'Intermediate Lesson'),
        ('advanced', 'Advanced Lesson'),
        ('test_prep', 'Test Preparation'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    plan = models.ForeignKey(LessonPlan, on_delete=models.SET_NULL, null=True, blank=True)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='beginner')
    special_requirements = models.TextField(blank=True)
    credits_used = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    duration_minutes = models.IntegerField(default=60)

    def __str__(self):
        return f"{self.student} - {self.scheduled_time}"

class Review(models.Model):
    student = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    image = models.ImageField(upload_to='reviews/', null=True, blank=True)
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