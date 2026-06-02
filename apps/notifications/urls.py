from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification routes belong to the currently logged-in user.
    path('', views.notifications_view, name='index'),
    path('<int:pk>/read/', views.notification_mark_read_view, name='read'),
]
