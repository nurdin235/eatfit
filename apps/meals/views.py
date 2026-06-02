from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import MealPlan, Meal
from .forms import MealPlanForm, MealForm
from apps.ai_services.services import OpenAIRecommendationService
from apps.groceries.services import GroceryGenerationService
from apps.notifications.services import ReminderService
from apps.nutrition.services import BudgetService, NutritionService
from apps.recipes.models import Recipe
from apps.users.services import assert_household_editor, get_active_household
from .services import MealAnalysisService, MealIngredientService


MEAL_SLOTS = ('breakfast', 'lunch', 'dinner', 'snack')

@login_required
def meal_plans_view(request):
    """List meal plans for the current user's household."""

    household = get_active_household(request.user)
    plans = MealPlan.objects.filter(household=household).order_by('-start_date')
    return render(request, 'meals/index.html', {'plans': plans})

@login_required
def create_meal_plan_view(request):
    """Handle GET for a blank form and POST for saving a new MealPlan."""

    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            meal_plan = form.save(commit=False)
            # commit=False gives the view a chance to attach household ownership.
            meal_plan.household = household
            meal_plan.created_by = request.user
            meal_plan.save()
            messages.success(request, "Meal plan created successfully. You can now add meals.")
            return redirect('meals:detail', pk=meal_plan.pk)
    else:
        form = MealPlanForm()
    
    return render(request, 'meals/create.html', {'form': form})

@login_required
def meal_plan_detail_view(request, pk):
    """Show a planner calendar and handle adding/replacing a meal slot."""

    household = get_active_household(request.user)
    meal_plan = get_object_or_404(MealPlan, pk=pk, household=household)
    meals = meal_plan.meals.select_related('recipe').prefetch_related('custom_ingredients', 'analysis').all().order_by('date', 'meal_type')
    recipes = Recipe.objects.filter(Q(is_public=True) | Q(household=household)).distinct().order_by('title')
    
    if request.method == 'POST':
        # POST means the user submitted the meal form from the right-hand panel.
        form = MealForm(request.POST)
        form.fields['recipe'].queryset = recipes
        if form.is_valid():
            assert_household_editor(request.user, household)
            meal_date = form.cleaned_data['date']
            if not meal_plan.start_date <= meal_date <= meal_plan.end_date:
                form.add_error('date', "Meal date must be inside this plan range.")
            elif form.cleaned_data['entry_type'] == 'custom' and not any(row.get('name', '').strip() for row in MealIngredientService.parse_rows(request.POST)):
                form.add_error('recipe_name', "Add at least one ingredient for a custom meal.")
            if form.errors:
                pass
            else:
                # A plan can have only one meal per date/type slot, so replacement
                # is implemented by deleting any existing row for that slot.
                Meal.objects.filter(
                    meal_plan=meal_plan,
                    date=meal_date,
                    meal_type=form.cleaned_data['meal_type'],
                ).delete()
                meal = form.save(commit=False)
                meal.meal_plan = meal_plan
                if meal.entry_type == 'custom':
                    meal.recipe = None
                    meal.recipe_name = form.cleaned_data['recipe_name'].strip()
                else:
                    meal.recipe_name = meal.recipe.title if meal.recipe else ''
                meal.save()
                if meal.entry_type == 'custom':
                    # Extra custom ingredient rows are normal HTML arrays, parsed by a service.
                    MealIngredientService.sync_from_form(meal, MealIngredientService.parse_rows(request.POST))
                MealAnalysisService().analyze(meal)
                ReminderService.schedule(meal)
                messages.success(request, "Meal saved and analyzed.")
                return redirect('meals:detail', pk=pk)
        if form.errors:
            messages.error(request, "Please review the meal fields.")
    else:
        form = MealForm(initial={'entry_type': 'custom', 'date': meal_plan.start_date})
        form.fields['recipe'].queryset = recipes

    meal_by_slot = {(meal.date, meal.meal_type): meal for meal in meals}
    planner_days = []
    current = meal_plan.start_date
    while current <= meal_plan.end_date:
        planner_days.append(
            {
                'date': current,
                'slots': [{'key': slot, 'label': slot.title(), 'meal': meal_by_slot.get((current, slot))} for slot in MEAL_SLOTS],
            }
        )
        current += timedelta(days=1)

    grocery_list = meal_plan.grocerylist_set.order_by('-created_at').first()
    nutrition = NutritionService.meal_plan_totals(meal_plan)
    budget = BudgetService.evaluate(meal_plan, grocery_list)
    recommendations = OpenAIRecommendationService().rank_recipes(request.user, limit=3)
    return render(request, 'meals/detail.html', {
        'meal_plan': meal_plan,
        'planner_days': planner_days,
        'meals': meals,
        'form': form,
        'grocery_list': grocery_list,
        'nutrition': nutrition,
        'budget': budget,
        'recommendations': recommendations,
        'ingredient_row_numbers': range(3),
    })

@login_required
def delete_meal_view(request, pk, meal_pk):
    household = get_active_household(request.user)
    meal_plan = get_object_or_404(MealPlan, pk=pk, household=household)
    meal = get_object_or_404(Meal, pk=meal_pk, meal_plan=meal_plan)
    if request.method == 'POST':
        assert_household_editor(request.user, household)
        meal.delete()
        messages.success(request, "Meal removed.")
    return redirect('meals:detail', pk=meal_plan.pk)


@login_required
def generate_grocery_list_view(request, pk):
    """Generate a grocery list from the meals in one plan."""

    household = get_active_household(request.user)
    meal_plan = get_object_or_404(MealPlan, pk=pk, household=household)
    if request.method == 'POST':
        assert_household_editor(request.user, household)
        grocery_list = GroceryGenerationService.generate(meal_plan, request.user)
        budget = BudgetService.evaluate(meal_plan, grocery_list)
        if budget['is_over_budget']:
            messages.warning(request, f"Grocery list generated, but it is over budget by {abs(budget['remaining_xaf']):,.0f} XAF.")
        else:
            messages.success(request, "Grocery list generated and budget checked.")
        return redirect('groceries:detail', pk=grocery_list.pk)
    return redirect('meals:detail', pk=pk)


@login_required
def ingredient_row_view(request):
    return render(request, 'meals/partials/ingredient_row.html')


@login_required
def analyze_meal_view(request, pk, meal_pk):
    household = get_active_household(request.user)
    meal_plan = get_object_or_404(MealPlan, pk=pk, household=household)
    meal = get_object_or_404(Meal, pk=meal_pk, meal_plan=meal_plan)
    if request.method == 'POST':
        assert_household_editor(request.user, household)
        MealAnalysisService().analyze(meal)
        messages.success(request, "Meal analysis refreshed.")
    return redirect('meals:detail', pk=pk)
