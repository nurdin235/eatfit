from collections import defaultdict

from apps.users.models import Profile


class NutritionService:
    @staticmethod
    def calculate_recipe(recipe):
        totals = defaultdict(float)
        estimated_cost = 0
        for item in recipe.ingredients.select_related('ingredient'):
            ingredient = item.ingredient
            quantity = item.quantity
            totals['calories'] += ingredient.calories_per_unit * quantity
            totals['protein'] += ingredient.protein_per_unit * quantity
            totals['carbs'] += ingredient.carbs_per_unit * quantity
            totals['fat'] += ingredient.fat_per_unit * quantity
            estimated_cost += float(ingredient.estimated_cost_per_unit_xaf) * quantity

        recipe.calories = round(totals['calories'], 1)
        recipe.protein = round(totals['protein'], 1)
        recipe.carbs = round(totals['carbs'], 1)
        recipe.fat = round(totals['fat'], 1)
        recipe.estimated_cost_xaf = round(estimated_cost, 2)
        recipe.save(update_fields=['calories', 'protein', 'carbs', 'fat', 'estimated_cost_xaf'])
        return {
            'calories': recipe.calories,
            'protein': recipe.protein,
            'carbs': recipe.carbs,
            'fat': recipe.fat,
            'estimated_cost_xaf': float(recipe.estimated_cost_xaf),
        }

    @staticmethod
    def meal_totals(meal):
        if meal.entry_type == 'recipe' and meal.recipe:
            multiplier = meal.servings / max(meal.recipe.servings, 1)
            return {
                'calories': round(meal.recipe.calories * multiplier, 1),
                'protein': round(meal.recipe.protein * multiplier, 1),
                'carbs': round(meal.recipe.carbs * multiplier, 1),
                'fat': round(meal.recipe.fat * multiplier, 1),
            }
        if hasattr(meal, 'analysis'):
            return {
                'calories': meal.analysis.calories,
                'protein': meal.analysis.protein,
                'carbs': meal.analysis.carbs,
                'fat': meal.analysis.fat,
            }
        totals = defaultdict(float)
        for item in meal.custom_ingredients.select_related('ingredient'):
            if item.ingredient_id:
                totals['calories'] += item.ingredient.calories_per_unit * item.quantity
                totals['protein'] += item.ingredient.protein_per_unit * item.quantity
                totals['carbs'] += item.ingredient.carbs_per_unit * item.quantity
                totals['fat'] += item.ingredient.fat_per_unit * item.quantity
        return {key: round(value, 1) for key, value in totals.items()}

    @staticmethod
    def meal_plan_totals(meal_plan):
        totals = defaultdict(float)
        meals = meal_plan.meals.select_related('recipe').prefetch_related('custom_ingredients__ingredient').all()
        for meal in meals:
            meal_totals = NutritionService.meal_totals(meal)
            totals['calories'] += meal_totals.get('calories', 0)
            totals['protein'] += meal_totals.get('protein', 0)
            totals['carbs'] += meal_totals.get('carbs', 0)
            totals['fat'] += meal_totals.get('fat', 0)
        return {key: round(value, 1) for key, value in totals.items()}


class BudgetService:
    @staticmethod
    def evaluate(meal_plan, grocery_list=None):
        household = meal_plan.household
        owner = meal_plan.created_by
        default_budget = None
        if owner:
            profile, _ = Profile.objects.get_or_create(user=owner)
            default_budget = profile.weekly_budget_xaf
        budget = meal_plan.weekly_budget_xaf or default_budget or 35000
        if grocery_list is None:
            grocery_list = meal_plan.grocerylist_set.order_by('-created_at').first()
        total = float(grocery_list.total_estimated_cost_xaf) if grocery_list else 0
        return {
            'household': household,
            'budget_xaf': budget,
            'total_xaf': total,
            'remaining_xaf': round(budget - total, 2),
            'is_over_budget': total > budget,
        }
