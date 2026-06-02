from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import UserSerializer

app_name = 'users_api'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    # A small "who am I" endpoint for authenticated API clients.
    return Response(UserSerializer(request.user).data)


urlpatterns = [
    path('me/', me, name='me'),
]
