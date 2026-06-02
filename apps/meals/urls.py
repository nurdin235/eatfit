from django.urls import path
from . import views

app_name = 'meals'

urlpatterns = [
    # /meal-plans/ shows the list; nested routes act on one selected plan.
    path('', views.meal_plans_view, name='index'),
    path('create/', views.create_meal_plan_view, name='create'),
    path('ingredient-row/', views.ingredient_row_view, name='ingredient_row'),
    path('<int:pk>/', views.meal_plan_detail_view, name='detail'),
    path('<int:pk>/meals/<int:meal_pk>/delete/', views.delete_meal_view, name='delete_meal'),
    path('<int:pk>/meals/<int:meal_pk>/analyze/', views.analyze_meal_view, name='analyze_meal'),
    path('<int:pk>/grocery-list/', views.generate_grocery_list_view, name='generate_grocery'),
]
