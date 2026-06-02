from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

app_name = 'notifications_api'


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    # request.user comes from DRF authentication and scopes the notification query.
    data = [
        {
            'id': item.id,
            'type': item.notification_type,
            'title': item.title,
            'message': item.message,
            'is_read': item.is_read,
            'scheduled_for': item.scheduled_for,
            'created_at': item.created_at,
        }
        for item in request.user.notifications.all()[:50]
    ]
    return Response(data)


urlpatterns = [
    path('', notification_list, name='list'),
]
