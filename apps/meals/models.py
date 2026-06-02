from decimal import Decimal

from django.db import models
from django.utils import timezone
from apps.users.models import User, Household
from apps.recipes.models import Ingredient, Recipe

class MealPlan(models.Model):
    """A dated plan for a household, usually one week of meal slots."""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        ARCHIVED = 'archived', 'Archived'

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='meal_plans')
    title = models.CharField(max_length=255, default='Weekly Meal Plan')
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_ai_generated = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    weekly_budget_xaf = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"

class Meal(models.Model):
    """One breakfast, lunch, dinner, or snack inside a MealPlan."""

    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    )
    SOURCES = (
        ('manual', 'Manual'),
        ('ai', 'AI suggested'),
    )
    ENTRY_TYPES = (
        ('recipe', 'Existing recipe'),
        ('custom', 'Custom meal'),
    )
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name='meals')
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES, default='recipe')
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    recipe_name = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField()
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    servings = models.IntegerField(default=1)
    source = models.CharField(max_length=20, choices=SOURCES, default='manual')
    is_ai_suggested = models.BooleanField(default=False)
    ai_reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['date', 'meal_type']
        constraints = [
            models.UniqueConstraint(fields=['meal_plan', 'date', 'meal_type'], name='unique_meal_slot'),
        ]

    def __str__(self):
        return self.recipe.title if self.recipe else (self.recipe_name or 'Unassigned meal')


class MealIngredient(models.Model):
    """Ingredient rows for custom meals that are not based on a saved recipe."""

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='custom_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    quantity = models.FloatField(default=0)
    unit = models.CharField(max_length=50, default='g')
    unit_price_xaf = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_price_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Keep total_price_xaf synchronized whenever quantity or unit price changes.
        if self.unit_price_xaf is not None:
            self.total_price_xaf = self.unit_price_xaf * Decimal(str(self.quantity))
        else:
            self.total_price_xaf = 0
        if not self.name and self.ingredient_id:
            self.name = self.ingredient.name
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity:g} {self.unit} {self.name}"


class MealAnalysis(models.Model):
    """Stored nutrition, cost, benefit, and risk summary for one meal."""

    class Status(models.TextChoices):
        LOCAL = 'local', 'Local calculation'
        AI = 'ai', 'AI estimated'
        FALLBACK = 'fallback', 'Fallback estimate'
        ERROR = 'error', 'Analysis error'

    meal = models.OneToOneField(Meal, on_delete=models.CASCADE, related_name='analysis')
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    estimated_total_cost_xaf = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nutrition_strength_score = models.FloatField(default=0)
    nutrition_strength = models.CharField(max_length=80, default='Needs review')
    health_benefits = models.JSONField(default=list, blank=True)
    health_risks = models.JSONField(default=list, blank=True)
    advisory_summary = models.TextField(blank=True)
    limitations = models.JSONField(default=list, blank=True)
    confidence = models.FloatField(default=0)
    is_estimated = models.BooleanField(default=True)
    provider = models.CharField(max_length=50, default='local')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.LOCAL)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Analysis for {self.meal}"
