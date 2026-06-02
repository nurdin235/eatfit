from django.utils import timezone

from config.celery import app

from .models import Notification


@app.task
def mark_due_notifications_sent():
    now = timezone.now()
    return Notification.objects.filter(scheduled_for__lte=now, sent_at__isnull=True).update(sent_at=now)
