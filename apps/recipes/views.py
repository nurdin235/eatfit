from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.nutrition.services import NutritionService
from apps.users.services import assert_household_editor, get_active_household

from .forms import RecipeForm, RecipeIngredientFormSet
from .models import Recipe

@login_required
def recipes_view(request):
    """List public recipes plus private recipes for the active household."""

    household = get_active_household(request.user)
    query = request.GET.get('q', '').strip()
    recipes = Recipe.objects.filter(Q(is_public=True) | Q(household=household)).distinct()
    if query:
        recipes = recipes.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(cuisine__icontains=query)
            | Q(diet_type__icontains=query)
        )
    return render(request, 'recipes/index.html', {'recipes': recipes.order_by('title'), 'query': query})


@login_required
def recipe_detail_view(request, pk):
    household = get_active_household(request.user)
    recipe = get_object_or_404(Recipe.objects.prefetch_related('ingredients__ingredient'), Q(is_public=True) | Q(household=household), pk=pk)
    return render(request, 'recipes/detail.html', {'recipe': recipe})


@login_required
def recipe_create_view(request):
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    return _recipe_form(request)


@login_required
def recipe_edit_view(request, pk):
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    recipe = get_object_or_404(Recipe, pk=pk, household=household)
    return _recipe_form(request, recipe)


@login_required
def recipe_delete_view(request, pk):
    household = get_active_household(request.user)
    recipe = get_object_or_404(Recipe, pk=pk, household=household)
    if request.method == 'POST':
        assert_household_editor(request.user, household)
        recipe.delete()
        messages.success(request, "Recipe deleted.")
        return redirect('recipes:index')
    return render(request, 'recipes/confirm_delete.html', {'recipe': recipe})


def _recipe_form(request, recipe=None):
    """Shared create/edit logic for RecipeForm and its ingredient formset."""

    household = get_active_household(request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            # The form saves recipe fields; the view supplies ownership fields.
            recipe.created_by = recipe.created_by or request.user
            recipe.household = household
            recipe.save()
            formset.instance = recipe
            formset.save()
            NutritionService.calculate_recipe(recipe)
            messages.success(request, "Recipe saved.")
            return redirect('recipes:detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'recipes/form.html', {'form': form, 'formset': formset, 'recipe': recipe})
