from django import forms

ROLE_CHOICES = (
    ('client', 'Client'),
    ('freelancer', 'Freelancer'),
)

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'border rounded px-3 py-2 w-full',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'border rounded px-3 py-2 w-full',
        'placeholder': 'Password'
    }))

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)

from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'budget',
            'skills_required',
            'deadline',
            'duration',
        ]
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'skills_required': forms.CheckboxSelectMultiple(),
        }
