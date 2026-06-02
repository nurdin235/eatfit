from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from apps.meals.models import MealPlan
from apps.users.models import Profile
from apps.users.services import get_active_household

from .services import BudgetService, NutritionService

@login_required
def nutrition_view(request):
    """Show nutrition totals for the latest household meal plan."""

    household = get_active_household(request.user)
    plan = MealPlan.objects.filter(household=household).order_by('-start_date').first()
    totals = NutritionService.meal_plan_totals(plan) if plan else {}
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return render(request, 'nutrition/index.html', {'plan': plan, 'totals': totals, 'profile': profile})


@login_required
def budget_view(request):
    """Compare recent meal plans with their generated grocery costs."""

    household = get_active_household(request.user)
    plans = MealPlan.objects.filter(household=household).order_by('-start_date')[:8]
    evaluations = []
    for plan in plans:
        grocery_list = plan.grocerylist_set.order_by('-created_at').first()
        evaluations.append({'plan': plan, 'grocery_list': grocery_list, 'budget': BudgetService.evaluate(plan, grocery_list)})
    return render(request, 'nutrition/budget.html', {'evaluations': evaluations})
