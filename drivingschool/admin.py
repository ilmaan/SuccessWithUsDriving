from django.contrib import admin
from .models import (
    Student, Instructor, LessonPlan, PlanFeature, Appointment, 
    Review, JobApplication, GiftCard, Referral
)

# Register your models here.

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'license_status', 'total_credits', 'created_at')
    list_filter = ('license_status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    readonly_fields = ('created_at',)

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'experience_years', 'rating', 'is_available')
    list_filter = ('is_available', 'experience_years', 'rating')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')
    list_editable = ('is_available',)

class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 3
    fields = ('feature_text', 'order')

@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'hours', 'price', 'original_price', 'package_type', 'is_popular', 'includes_test', 'is_active', 'display_order')
    list_filter = ('is_popular', 'includes_test', 'package_type', 'is_active', 'hours')
    search_fields = ('name', 'description')
    list_editable = ('is_popular', 'includes_test', 'price', 'original_price', 'is_active', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlanFeatureInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'package_type')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'hours')
        }),
        ('Settings', {
            'fields': ('is_popular', 'includes_test', 'is_active', 'display_order')
        }),
    )

@admin.register(PlanFeature)
class PlanFeatureAdmin(admin.ModelAdmin):
    list_display = ('plan', 'feature_text', 'order')
    list_filter = ('plan',)
    search_fields = ('feature_text', 'plan__name')
    list_editable = ('order',)

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'instructor', 'plan', 'scheduled_time', 'status', 'credits_used')
    list_filter = ('status', 'scheduled_time', 'plan')
    search_fields = ('student__user__username', 'instructor__user__username')
    date_hierarchy = 'scheduled_time'
    list_editable = ('status',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'instructor', 'rating', 'created_at', 'image')
    list_filter = ('rating', 'created_at')
    search_fields = ('student', 'instructor', 'comment')
    readonly_fields = ('created_at',)

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'applied_at')
    list_filter = ('applied_at',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('applied_at',)

@admin.register(GiftCard)
class GiftCardAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'is_used', 'used_by', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('code', 'used_by__username')
    readonly_fields = ('created_at',)
    list_editable = ('is_used',)

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('referrer', 'referred_email', 'is_converted', 'created_at')
    list_filter = ('is_converted', 'created_at')
    search_fields = ('referrer__username', 'referred_email')
    readonly_fields = ('created_at',)
    list_editable = ('is_converted',)
