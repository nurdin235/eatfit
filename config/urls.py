from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.nutrition import views as nutrition_views
from apps.users import views as user_views

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    # Browser page routes. include() delegates each feature area to its app urls.py.
    path('', include('apps.core.urls')),
    path('auth/', include('apps.users.auth_urls')),
    path('profile/', user_views.profile_view, name='profile'),
    path('households/', user_views.household_view, name='households'),
    path('meal-plans/', include('apps.meals.urls')),
    path('groceries/', include('apps.groceries.urls')),
    path('pantry/', include('apps.pantry.urls')),
    path('recipes/', include('apps.recipes.urls')),
    path('nutrition/', include('apps.nutrition.urls')),
    path('budget/', nutrition_views.budget_view, name='budget'),
    path('notifications/', include('apps.notifications.urls')),

    # JSON API routes. JWT endpoints issue access tokens for non-browser clients.
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/meal-plans/', include('apps.meals.api_urls')),
    path('api/v1/recipes/', include('apps.recipes.api_urls')),
    path('api/v1/grocery-lists/', include('apps.groceries.api_urls')),
    path('api/v1/notifications/', include('apps.notifications.api_urls')),
    path('api/v1/ai/', include('apps.ai_services.urls')),
]
