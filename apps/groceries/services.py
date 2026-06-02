from collections import defaultdict
from decimal import Decimal

from django.db import transaction

from apps.pantry.models import PantryItem
from apps.recipes.models import Ingredient

from .models import GroceryItem, GroceryList


class GroceryGenerationService:
    @staticmethod
    @transaction.atomic
    def generate(meal_plan, generated_by=None):
        # atomic means either the list and all items save together, or none save.
        grocery_list = GroceryList.objects.create(
            household=meal_plan.household,
            meal_plan=meal_plan,
            generated_by=generated_by,
        )

        required = defaultdict(float)
        ingredients = {}
        units = {}

        for meal in meal_plan.meals.select_related('recipe').prefetch_related('recipe__ingredients__ingredient', 'custom_ingredients__ingredient'):
            # Recipe meals reuse structured ingredients; custom meals use their own rows.
            if meal.entry_type == 'recipe' and meal.recipe:
                recipe = meal.recipe
                serving_multiplier = meal.servings / max(recipe.servings, 1)
                for recipe_item in recipe.ingredients.all():
                    key = (recipe_item.ingredient_id, recipe_item.unit)
                    ingredients[key] = recipe_item.ingredient
                    units[key] = recipe_item.unit
                    required[key] += recipe_item.quantity * serving_multiplier
                continue

            for custom_item in meal.custom_ingredients.all():
                ingredient = custom_item.ingredient
                if ingredient is None:
                    unit_price = custom_item.unit_price_xaf or 0
                    ingredient, _ = Ingredient.objects.get_or_create(
                        name=custom_item.name,
                        defaults={
                            'category': 'custom',
                            'default_unit': custom_item.unit,
                            'estimated_cost_per_unit_xaf': unit_price,
                        },
                    )
                key = (ingredient.id, custom_item.unit)
                ingredients[key] = ingredient
                units[key] = custom_item.unit
                required[key] += custom_item.quantity

        pantry = defaultdict(float)
        # Pantry quantities reduce what the user still needs to buy.
        for item in PantryItem.objects.filter(household=meal_plan.household):
            pantry[(item.ingredient_id, item.unit)] += item.quantity

        total = Decimal('0')
        for key, quantity in required.items():
            ingredient = ingredients[key]
            needed_quantity = max(quantity - pantry.get(key, 0), 0)
            estimated_cost = Decimal(str(needed_quantity)) * ingredient.estimated_cost_per_unit_xaf
            total += estimated_cost
            GroceryItem.objects.create(
                grocery_list=grocery_list,
                ingredient=ingredient,
                quantity=round(needed_quantity, 2),
                unit=units[key],
                estimated_cost_xaf=estimated_cost.quantize(Decimal('0.01')),
                is_optional=needed_quantity == 0,
            )

        grocery_list.total_estimated_cost_xaf = total.quantize(Decimal('0.01'))
        grocery_list.save(update_fields=['total_estimated_cost_xaf'])
        return grocery_list
