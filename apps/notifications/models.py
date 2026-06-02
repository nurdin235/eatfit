from django.db import models
from apps.users.models import User
from datetime import time

class Notification(models.Model):
    """An in-app message shown to a user, such as a meal reminder."""

    class Type(models.TextChoices):
        MEAL_REMINDER = 'meal_reminder', 'Meal reminder'
        GROCERY = 'grocery', 'Grocery'
        BUDGET = 'budget', 'Budget'
        SYSTEM = 'system', 'System'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField()
    action_url = models.CharField(max_length=255, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class NotificationPreference(models.Model):
    """User-specific reminder settings used when meals are scheduled."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    meal_reminders_enabled = models.BooleanField(default=True)
    breakfast_time = models.TimeField(default=time(7, 30))
    lunch_time = models.TimeField(default=time(12, 30))
    dinner_time = models.TimeField(default=time(19, 0))
    reminder_minutes_before = models.PositiveIntegerField(default=30)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} notification preferences"
