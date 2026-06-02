from django.db.models import Q
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.services import get_active_household

from .models import Recipe
from .serializers import RecipeSerializer

app_name = 'recipes_api'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recipe_list(request):
    # Public recipes are shared; private recipes are limited to the user's household.
    household = get_active_household(request.user)
    recipes = Recipe.objects.filter(Q(is_public=True) | Q(household=household)).distinct()
    return Response(RecipeSerializer(recipes, many=True).data)


urlpatterns = [
    path('', recipe_list, name='list'),
]
