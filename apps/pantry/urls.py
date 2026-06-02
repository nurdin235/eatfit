from django.urls import path
from . import views

app_name = 'pantry'

urlpatterns = [
    # Pantry has the classic CRUD shape: list, add, edit, delete.
    path('', views.pantry_view, name='index'),
    path('add/', views.pantry_add_view, name='add'),
    path('<int:pk>/edit/', views.pantry_edit_view, name='edit'),
    path('<int:pk>/delete/', views.pantry_delete_view, name='delete'),
]
