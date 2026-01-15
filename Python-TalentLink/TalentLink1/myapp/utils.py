# myapp/utils.py
from django.core.mail import send_mail
from .models import Notification

def send_notification(user, message, email_placeholder=False):
    # Save in-app notification
    Notification.objects.create(user=user, message=message)

    # Email placeholder (won’t actually send in dev)
    if email_placeholder:
        send_mail(
            subject="Notification",
            message=message,
            from_email="noreply@yourapp.com",
            recipient_list=[user.email],
            fail_silently=True
        )
# myapp/utils.py
from .models import Notification

def notify_user(user, message):
    """
    Creates a notification for the given user.
    """
    Notification.objects.create(user=user, message=message)
