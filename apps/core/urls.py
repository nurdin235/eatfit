from django.urls import path
from . import views

urlpatterns = [
    # The empty path is the dashboard because config.urls includes this at site root.
    path('healthz/', views.healthz, name='healthz'),
    path('', views.dashboard, name='dashboard'),
]
