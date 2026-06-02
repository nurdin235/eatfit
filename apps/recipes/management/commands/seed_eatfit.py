from django.core.management.base import BaseCommand

from apps.nutrition.services import NutritionService
from apps.recipes.models import Ingredient, Recipe, RecipeIngredient


INGREDIENTS = [
    ('Bitter leaves', 'vegetable', 'g', 4, 0.4, 0.03, 0.07, 0.01),
    ('Groundnuts', 'protein', 'g', 6, 5.7, 0.26, 0.16, 0.49),
    ('Plantain', 'produce', 'g', 2, 1.2, 0.01, 0.32, 0.0),
    ('Palm oil', 'oil', 'ml', 3, 8.8, 0.0, 0.0, 1.0),
    ('Eru leaves', 'vegetable', 'g', 5, 0.5, 0.04, 0.08, 0.01),
    ('Water fufu', 'grain', 'g', 1, 1.4, 0.01, 0.34, 0.0),
    ('Chicken', 'protein', 'g', 8, 2.4, 0.27, 0.0, 0.14),
    ('Rice', 'grain', 'g', 2, 1.3, 0.03, 0.28, 0.0),
    ('Tomatoes', 'produce', 'g', 2, 0.2, 0.01, 0.04, 0.0),
    ('Beans', 'protein', 'g', 3, 3.4, 0.21, 0.62, 0.01),
    ('Flour', 'grain', 'g', 2, 3.6, 0.1, 0.76, 0.01),
]

RECIPES = [
    {
        'title': 'Ndole with Plantains',
        'description': 'A Cameroonian stew with bitter leaves, groundnuts, and ripe plantains.',
        'instructions': 'Wash bitter leaves. Simmer groundnuts with spices. Fold in leaves and palm oil. Serve with boiled plantains.',
        'servings': 4,
        'prep_time': 30,
        'cook_time': 60,
        'tags': ['high protein', 'traditional'],
        'ingredients': [('Bitter leaves', 400, 'g'), ('Groundnuts', 250, 'g'), ('Plantain', 1000, 'g'), ('Palm oil', 120, 'ml')],
    },
    {
        'title': 'Eru and Water Fufu',
        'description': 'South West Cameroonian eru leaves served with water fufu.',
        'instructions': 'Cook proteins until tender. Add eru leaves, palm oil, and seasoning. Serve hot with water fufu.',
        'servings': 4,
        'prep_time': 25,
        'cook_time': 55,
        'tags': ['traditional', 'family'],
        'ingredients': [('Eru leaves', 350, 'g'), ('Chicken', 500, 'g'), ('Palm oil', 100, 'ml'), ('Water fufu', 1000, 'g')],
    },
    {
        'title': 'Poulet DG with Rice',
        'description': 'Chicken, vegetables, plantains, and rice for a filling household meal.',
        'instructions': 'Brown chicken. Fry plantains. Cook tomato sauce. Combine and serve with rice.',
        'servings': 4,
        'prep_time': 20,
        'cook_time': 50,
        'tags': ['popular', 'budget aware'],
        'ingredients': [('Chicken', 700, 'g'), ('Plantain', 800, 'g'), ('Tomatoes', 300, 'g'), ('Rice', 600, 'g')],
    },
    {
        'title': 'Beans and Puff Puff',
        'description': 'Classic Cameroonian breakfast pairing savory beans with sweet fried dough.',
        'instructions': 'Stew beans until soft. Mix flour dough and fry small portions until golden.',
        'servings': 4,
        'prep_time': 40,
        'cook_time': 45,
        'tags': ['breakfast', 'low cost'],
        'ingredients': [('Beans', 500, 'g'), ('Flour', 400, 'g'), ('Palm oil', 80, 'ml')],
    },
]


class Command(BaseCommand):
    help = 'Seed local Cameroonian ingredients and recipes for EatFit demos.'

    def handle(self, *args, **options):
        ingredient_map = {}
        for name, category, unit, cost, calories, protein, carbs, fat in INGREDIENTS:
            ingredient, _ = Ingredient.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'default_unit': unit,
                    'estimated_cost_per_unit_xaf': cost,
                    'calories_per_unit': calories,
                    'protein_per_unit': protein,
                    'carbs_per_unit': carbs,
                    'fat_per_unit': fat,
                },
            )
            ingredient_map[name] = ingredient

        for source in RECIPES:
            data = source.copy()
            ingredients = data.pop('ingredients')
            recipe, _ = Recipe.objects.update_or_create(
                title=data['title'],
                defaults={**data, 'cuisine': 'Cameroonian', 'diet_type': 'none', 'is_cameroonian': True, 'is_public': True},
            )
            for ingredient_name, quantity, unit in ingredients:
                RecipeIngredient.objects.update_or_create(
                    recipe=recipe,
                    ingredient=ingredient_map[ingredient_name],
                    unit=unit,
                    defaults={'quantity': quantity},
                )
            NutritionService.calculate_recipe(recipe)

        self.stdout.write(self.style.SUCCESS('EatFit demo data seeded.'))
