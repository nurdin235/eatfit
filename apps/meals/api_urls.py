from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.services import get_active_household

from .models import MealPlan
from .serializers import MealPlanSerializer

app_name = 'meals_api'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meal_plan_list(request):
    # API clients only receive meal plans from the active household.
    household = get_active_household(request.user)
    plans = MealPlan.objects.filter(household=household)
    return Response(MealPlanSerializer(plans, many=True).data)


urlpatterns = [
    path('', meal_plan_list, name='list'),
]
