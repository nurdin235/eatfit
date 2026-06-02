from django.db import models
from apps.users.models import User
from apps.meals.models import Meal

class NutritionLog(models.Model):
    """Optional per-user daily nutrition record."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_logs')
    meal = models.ForeignKey(Meal, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    calories = models.FloatField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} nutrition on {self.date}"


class Budget(models.Model):
    """Stores a user's budget for a household and date range."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    household = models.ForeignKey('users.Household', on_delete=models.CASCADE, related_name='budgets')
    period_start = models.DateField()
    period_end = models.DateField()
    amount_xaf = models.PositiveIntegerField(default=35000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-period_start']

    def __str__(self):
        return f"{self.amount_xaf} XAF ({self.period_start} - {self.period_end})"
