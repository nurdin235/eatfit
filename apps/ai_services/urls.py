from django.urls import path
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle

from .services import OpenAIRecommendationService

app_name = 'ai_api'


class AIRecommendationThrottle(UserRateThrottle):
    scope = 'ai_recommendations'
    rate = '25/day'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@throttle_classes([AIRecommendationThrottle])
def recommendations(request):
    # DRF turns this Python list of dictionaries into JSON for API clients.
    ranked = OpenAIRecommendationService().rank_recipes(request.user)
    return Response(
        [
            {
                'recipe_id': item['recipe'].id,
                'title': item['recipe'].title,
                'score': item['score'],
                'reason': item['reason'],
            }
            for item in ranked
        ]
    )


urlpatterns = [
    path('recommendations/', recommendations, name='recommendations'),
]
