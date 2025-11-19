# driving_school/forms.py
from django import forms
from django.contrib.auth.models import User
from .models import *

class RegistrationForm(forms.Form):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    street_address = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    state = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    zip_code = forms.CharField(max_length=10, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    permit_no = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists. Please choose a different one.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered. Please use a different email or login.')
        return email

    def clean_state(self):
        state = (self.cleaned_data.get('state') or '').strip().lower()
        # Enforce California only
        if state not in ['california', 'ca']:
            raise forms.ValidationError('Sorry currently we do not serve in your area')
        # Normalize display value
        return 'California'

    def clean_zip_code(self):
        raw_zip = (self.cleaned_data.get('zip_code') or '').strip()
        # Accept only digits
        if not raw_zip.isdigit():
            raise forms.ValidationError('Sorry currently we do not serve in your area')
        zip_str = f"{int(raw_zip):05d}"
        # Allowed ZIP codes only
        allowed_zips = {
            '95050','95051','95054','95110','95112','95117','95126','95128','95129','95130',
            '95131','95132','95133','95134','95136','95014','95015','94085','94086','94087',
            '94089','94040','94041','94043','95035','95008','95009','95030','95032','95070',
            '95002','94301','94303','94304','94306'
        }
        if zip_str not in allowed_zips:
            raise forms.ValidationError('Sorry currently we do not serve in your area')
        return zip_str

    def save(self):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        Student.objects.create(
            user=user,
            phone=self.cleaned_data['phone'],
            street_address=self.cleaned_data['street_address'],
            city=self.cleaned_data['city'],
            state=self.cleaned_data['state'],
            zip_code=self.cleaned_data['zip_code'],
            permit_no=self.cleaned_data['permit_no']
        )
        return user

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['instructor', 'plan', 'scheduled_time']
        widgets = {
            'scheduled_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['first_name', 'last_name', 'email', 'phone', 'cv']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number (optional)'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx'
            })
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
        }