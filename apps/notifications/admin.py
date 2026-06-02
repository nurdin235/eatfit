from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # Admin filters help review unread reminders and notification types.
    list_display = ('user', 'notification_type', 'title', 'scheduled_for', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'message', 'user__username')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'meal_reminders_enabled', 'breakfast_time', 'lunch_time', 'dinner_time')
