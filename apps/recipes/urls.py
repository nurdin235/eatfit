from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    # These route names are used by templates with the {% url %} tag.
    path('', views.recipes_view, name='index'),
    path('new/', views.recipe_create_view, name='create'),
    path('<int:pk>/', views.recipe_detail_view, name='detail'),
    path('<int:pk>/edit/', views.recipe_edit_view, name='edit'),
    path('<int:pk>/delete/', views.recipe_delete_view, name='delete'),
]
