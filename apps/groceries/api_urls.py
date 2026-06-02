from django.shortcuts import get_object_or_404
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.meals.models import MealPlan
from apps.users.services import assert_household_editor, get_active_household

from .serializers import GroceryListSerializer
from .services import GroceryGenerationService

app_name = 'groceries_api'


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_grocery_list(request):
    # The API still filters by household so users cannot generate from another plan.
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    meal_plan = get_object_or_404(MealPlan, pk=request.data.get('meal_plan_id'), household=household)
    grocery_list = GroceryGenerationService.generate(meal_plan, request.user)
    return Response(GroceryListSerializer(grocery_list).data, status=201)


urlpatterns = [
    path('generate/', generate_grocery_list, name='generate'),
]
