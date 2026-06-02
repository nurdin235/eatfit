from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import NotificationPreferenceForm
from .models import Notification, NotificationPreference


@login_required
def notifications_view(request):
    """Display the user's inbox and save reminder preferences."""

    notifications = request.user.notifications.all()
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = NotificationPreferenceForm(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification preferences updated.")
            return redirect('notifications:index')
    else:
        form = NotificationPreferenceForm(instance=prefs)
    return render(request, 'notifications/index.html', {'notifications': notifications, 'form': form})


@login_required
def notification_mark_read_view(request, pk):
    """Mark one notification as read, but only if it belongs to the user."""

    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == 'POST':
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return redirect('notifications:index')
