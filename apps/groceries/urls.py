from django.urls import path
from . import views

app_name = 'groceries'

urlpatterns = [
    # Grocery lists are generated from meal plans, then items can be edited or toggled.
    path('', views.groceries_view, name='index'),
    path('<int:pk>/', views.grocery_detail_view, name='detail'),
    path('<int:pk>/items/<int:item_pk>/edit/', views.grocery_item_update_view, name='item_edit'),
    path('<int:pk>/items/<int:item_pk>/toggle/', views.grocery_item_toggle_view, name='item_toggle'),
]
