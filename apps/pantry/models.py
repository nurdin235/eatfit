from django.db import models
from apps.users.models import Household
from apps.recipes.models import Ingredient

class PantryItem(models.Model):
    """Ingredient stock already available in the household kitchen."""

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='pantry_items')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField()
    unit = models.CharField(max_length=50)
    expiry_date = models.DateField(null=True, blank=True)
    low_stock_threshold = models.FloatField(default=0)

    class Meta:
        ordering = ['ingredient__name']
        constraints = [
            models.UniqueConstraint(fields=['household', 'ingredient', 'unit'], name='unique_pantry_item_unit'),
        ]

    @property
    def is_low_stock(self):
        # Templates use this property to show a low-stock warning badge.
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.ingredient.name} - {self.quantity:g} {self.unit}"
