from django import forms

from .models import NotificationPreference


class NotificationPreferenceForm(forms.ModelForm):
    """Form for changing when meal reminder notifications are created."""

    class Meta:
        model = NotificationPreference
        fields = [
            'meal_reminders_enabled',
            'breakfast_time',
            'lunch_time',
            'dinner_time',
            'reminder_minutes_before',
        ]
        widgets = {
            'breakfast_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'lunch_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'dinner_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'reminder_minutes_before': forms.NumberInput(attrs={'class': 'form-input', 'min': '0', 'max': '240'}),
        }
