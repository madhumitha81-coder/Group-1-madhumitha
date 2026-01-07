from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from .models import Project, Skill

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
# PROJECT FORM
# -------------------------
class ProjectForm(forms.ModelForm):
    skills_text = forms.CharField(
        required=False,
        label="Skills Required",
        widget=forms.TextInput(attrs={
            "placeholder": "Python, Django, React"
        })
    )

    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "budget",
            "deadline",
            "duration",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show existing skills when editing
        if self.instance.pk:
            self.fields["skills_text"].initial = ", ".join(
                skill.name for skill in self.instance.skills_required.all()
            )

    def save(self, commit=True):
        project = super().save(commit=False)

        if commit:
            project.save()   # ✅ MUST SAVE FIRST (get ID)

            # Handle skills safely AFTER save
            skills_text = self.cleaned_data.get("skills_text", "")
            skills = [s.strip() for s in skills_text.split(",") if s.strip()]

            project.skills_required.clear()

            for skill_name in skills:
                skill, _ = Skill.objects.get_or_create(name=skill_name)
                project.skills_required.add(skill)

        return project
