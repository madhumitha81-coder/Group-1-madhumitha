from django.db import models
from django.contrib.auth.models import User

# -------------------------
# Choices
# -------------------------




class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Profile(models.Model):
    ROLE_CHOICES = (
        ("client", "Client"),
        ("freelancer", "Freelancer"),
    )

    

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    name = models.CharField(max_length=100, blank=True, null=True)  # ← IMPORTANT
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    portfolio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    availability = models.BooleanField(default=True)
    location = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username


# -------------------------
# Project Model
# -------------------------
class Project(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    deadline = models.DateField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# -------------------------
# Task Model
# -------------------------
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    
    # Assign to a freelancer
    assigned_to = models.ForeignKey(
        Profile, 
        limit_choices_to={'role': 'freelancer'},
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='tasks'
    )
    
    # Optional link to a project
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tasks'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {'Completed' if self.completed else 'Pending'}"

# -------------------------
# Proposal Model
# -------------------------
class Proposal(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    freelancer = models.ForeignKey(Profile, limit_choices_to={'role': 'freelancer'}, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer.name} - {self.project.title}"

# -------------------------
# Contract Model
# -------------------------
class Contract(models.Model):
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Contract for {self.proposal.project.title}"

# -------------------------
# Message Model
# -------------------------
class Message(models.Model):
    sender = models.ForeignKey(Profile, limit_choices_to={'role': 'freelancer'}, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(Profile, limit_choices_to={'role': 'freelancer'}, on_delete=models.CASCADE, related_name="received_messages")
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.name} to {self.receiver.name}"

# -------------------------
# Review Model
# -------------------------
class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.project.title}"
