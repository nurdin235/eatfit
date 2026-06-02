from django.db import models
from apps.users.models import Household
from apps.recipes.models import Ingredient
from apps.meals.models import MealPlan

class GroceryList(models.Model):
    """A shopping list generated from a household meal plan."""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        SHOPPING = 'shopping', 'Shopping'
        COMPLETED = 'completed', 'Completed'

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='grocery_lists')
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    total_estimated_cost_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.SET_NULL)
    is_ai_optimized = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Grocery list for {self.household} ({self.created_at:%Y-%m-%d})"

class GroceryItem(models.Model):
    """One ingredient line inside a GroceryList."""

    grocery_list = models.ForeignKey(GroceryList, on_delete=models.CASCADE, related_name='items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    estimated_cost_xaf = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    manually_adjusted = models.BooleanField(default=False)
    is_purchased = models.BooleanField(default=False)
    is_optional = models.BooleanField(default=False)

    class Meta:
        ordering = ['ingredient__category', 'ingredient__name']
        constraints = [
            models.UniqueConstraint(fields=['grocery_list', 'ingredient', 'unit'], name='unique_grocery_item_unit'),
        ]

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity:g} {self.unit}"
