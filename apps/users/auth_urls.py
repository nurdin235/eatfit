from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    # Authentication pages use normal Django sessions, not JWT.
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]
