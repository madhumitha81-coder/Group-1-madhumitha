from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------- Skills ----------------
class Skill(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# ---------------- Profile ----------------
class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('freelancer', 'Freelancer'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, blank=True)
    portfolio = models.TextField(blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    availability = models.BooleanField(default=True)
    location = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Default role is 'client'; registration form can override it
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


# ---------------- Project ----------------
class Project(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    deadline = models.DateField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True, help_text='Duration in days')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# ---------------- Proposal ----------------
class Proposal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='proposals')
    freelancer = models.ForeignKey(
        Profile,
        limit_choices_to={'role': 'freelancer'},
        on_delete=models.CASCADE,
        related_name='proposals'
    )
    cover_letter = models.TextField(blank=True, null=True)
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.freelancer.user.username} → {self.project.title}"


# ---------------- Contract ----------------
class Contract(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE)
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='client_contracts', null=True, blank=True)
    freelancer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='freelancer_contracts', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)


    
class Review(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    reviewer_name = models.CharField(max_length=100)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# ---------------- Task ----------------
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        Profile,
        limit_choices_to={'role': 'freelancer'},
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='tasks'
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True, related_name='tasks')
    completed = models.BooleanField(default=False)
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# ---------------- Message ----------------
class Message(models.Model):
    contract = models.ForeignKey(
        "Contract",
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey("Profile", on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)  # <-- add this
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def is_image(self):
        if self.file:
            return self.file.name.lower().endswith(
                (".png", ".jpg", ".jpeg", ".gif", ".webp")
            )
        return False

    def __str__(self):
        return f"{self.sender.user.username} - {self.contract.id}"
