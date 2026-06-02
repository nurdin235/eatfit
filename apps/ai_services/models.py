from django.db import models
from apps.users.models import User

class AIInteractionLog(models.Model):
    """Audit record for AI operations without storing raw prompts or responses."""

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Success'
        FALLBACK = 'fallback', 'Fallback'
        ERROR = 'error', 'Error'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    operation = models.CharField(max_length=255, default='unknown')
    provider = models.CharField(max_length=50, default='openai')
    model = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    input_hash = models.CharField(max_length=64, blank=True)
    output_summary = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.operation} ({self.status})"
