from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    # Nutrition pages are read-only summaries calculated from meal plans.
    path('', views.nutrition_view, name='index'),
    path('budget/', views.budget_view, name='budget'),
]
