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


from django import forms
from .models import Profile, Skill

class ProfileForm(forms.ModelForm):
    skills_text = forms.CharField(
        required=False,
        help_text="Enter skills separated by commas."
    )

    class Meta:
        model = Profile
        fields = ['avatar', 'name', 'bio', 'portfolio', 'location', 'availability']
        widgets = {
            'bio': forms.Textarea(attrs={'rows':3}),
            'portfolio': forms.Textarea(attrs={'rows':3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-fill skills_text from existing skills
        if self.instance.pk:
            self.fields['skills_text'].initial = ', '.join([s.name for s in self.instance.skills.all()])

    def save(self, commit=True):
        profile = super().save(commit=False)
        skills_str = self.cleaned_data.get('skills_text', '')
        skills_names = [s.strip() for s in skills_str.split(',') if s.strip()]
        if commit:
            profile.save()
            # Update skills
            profile.skills.clear()
            for skill_name in skills_names:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                profile.skills.add(skill)
        return profile

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
