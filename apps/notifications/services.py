from datetime import datetime, timedelta

from django.utils import timezone

from .models import Notification, NotificationPreference


class ReminderService:
    @staticmethod
    def schedule(meal):
        household = meal.meal_plan.household
        created = []
        meal_time_attr = f"{meal.meal_type}_time"
        for membership in household.memberships.select_related('user'):
            user = membership.user
            prefs, _ = NotificationPreference.objects.get_or_create(user=user)
            if not prefs.meal_reminders_enabled or not hasattr(prefs, meal_time_attr):
                continue
            meal_time = getattr(prefs, meal_time_attr)
            scheduled_for = datetime.combine(meal.date, meal_time) - timedelta(minutes=prefs.reminder_minutes_before)
            scheduled_for = timezone.make_aware(scheduled_for, timezone.get_current_timezone())
            notification, was_created = Notification.objects.get_or_create(
                user=user,
                notification_type=Notification.Type.MEAL_REMINDER,
                title=f"{meal.get_meal_type_display()} reminder",
                scheduled_for=scheduled_for,
                defaults={
                    'message': f"{meal} is planned for {meal.get_meal_type_display().lower()}.",
                    'action_url': f"/meal-plans/{meal.meal_plan_id}/",
                },
            )
            if was_created:
                created.append(notification)
        return created
