from django.db import models
from django.conf import settings
from django.utils import timezone

class Ingredient(models.Model):
    """A reusable food item with estimated cost and nutrition per unit."""

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, default='general')
    default_unit = models.CharField(max_length=50, default='g')
    estimated_cost_per_unit_xaf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    calories_per_unit = models.FloatField(default=0)
    protein_per_unit = models.FloatField(default=0)
    carbs_per_unit = models.FloatField(default=0)
    fat_per_unit = models.FloatField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.name

class Recipe(models.Model):
    """A reusable meal idea made from structured RecipeIngredient rows."""

    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    instructions = models.TextField()
    prep_time = models.IntegerField(help_text="in minutes")
    cook_time = models.IntegerField(help_text="in minutes")
    servings = models.IntegerField()
    diet_type = models.CharField(max_length=50, default='none')
    difficulty = models.CharField(max_length=20, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    cuisine = models.CharField(max_length=100, default='Cameroonian')
    allergens = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    estimated_cost_xaf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='recipes')
    household = models.ForeignKey('users.Household', null=True, blank=True, on_delete=models.CASCADE, related_name='recipes')
    is_public = models.BooleanField(default=True)
    is_cameroonian = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    @property
    def total_time(self):
        # Templates display this derived value without storing another database column.
        return self.prep_time + self.cook_time

class RecipeIngredient(models.Model):
    """Join table: one ingredient, its quantity, and unit inside one recipe."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient', 'unit'], name='unique_recipe_ingredient_unit'),
        ]

    def __str__(self):
        return f"{self.quantity:g} {self.unit} {self.ingredient.name}"
