from django.contrib import admin

from .models import Budget, NutritionLog


@admin.register(NutritionLog)
class NutritionLogAdmin(admin.ModelAdmin):
    # Staff can inspect saved nutrition logs by user and date.
    list_display = ('user', 'date', 'calories', 'protein', 'carbs', 'fat')
    list_filter = ('date',)


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'period_start', 'period_end', 'amount_xaf')
    list_filter = ('period_start',)
