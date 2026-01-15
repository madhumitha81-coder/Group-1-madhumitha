from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Project, Skill, Review


# -------------------------
# LOGIN FORM
# -------------------------
class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'border rounded px-3 py-2 w-full',
            'placeholder': 'Password'
        })
    )


# -------------------------
# USER REGISTER FORM
# -------------------------
ROLE_CHOICES = (
    ('client', 'Client'),
    ('freelancer', 'Freelancer'),
)

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=ROLE_CHOICES)


# -------------------------
# PROJECT FORM  ✅ FIXED
# -------------------------
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    skills_text = forms.CharField(required=False)

    class Meta:
        model = Project
        exclude = ["client"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"})
        }



# -------------------------
# REVIEW FORM
# -------------------------
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
