from django import forms
from django.contrib.auth.models import User
from .models import Customer

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['profile_photo', 'phone_number', 'address']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']