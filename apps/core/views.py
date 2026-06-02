from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import F

from apps.groceries.models import GroceryList
from apps.meals.models import Meal, MealPlan
from apps.nutrition.services import NutritionService
from apps.pantry.models import PantryItem
from apps.users.services import get_active_household

def healthz(request):
    """Read-only liveness endpoint for deployment checks."""

    return JsonResponse({'status': 'ok'})


def csrf_failure(request, reason=''):
    return render(request, 'base/csrf_failure.html', {'reason': reason}, status=403)


@login_required
def dashboard(request):
    """Home page after login: collect summary data from several apps."""

    household = get_active_household(request.user)
    # Query only the active household so users do not see another household's data.
    active_plan = MealPlan.objects.filter(household=household).order_by('-start_date').first()
    todays_meals = []
    nutrition = {}
    if active_plan:
        todays_meals = active_plan.meals.select_related('recipe').order_by('date', 'meal_type')[:6]
        nutrition = NutritionService.meal_plan_totals(active_plan)
    grocery_list = GroceryList.objects.filter(household=household).order_by('-created_at').first()
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    context = {
        'household': household,
        'active_plan': active_plan,
        'todays_meals': todays_meals,
        'nutrition': nutrition,
        'grocery_list': grocery_list,
        'low_stock_count': PantryItem.objects.filter(household=household, quantity__lte=F('low_stock_threshold')).count(),
        'unread_notifications': unread_notifications,
        'meal_count': Meal.objects.filter(meal_plan__household=household).count(),
    }
    return render(request, 'dashboard/dashboard.html', context)
