from django.contrib import admin

from .models import Meal, MealAnalysis, MealIngredient, MealPlan


class MealInline(admin.TabularInline):
    # Inline rows show meals directly inside a meal plan in the admin panel.
    model = Meal
    extra = 0


class MealIngredientInline(admin.TabularInline):
    model = MealIngredient
    extra = 0


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'household', 'start_date', 'end_date', 'status', 'created_by')
    list_filter = ('status', 'is_ai_generated')
    search_fields = ('title', 'household__name')
    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('meal_plan', 'date', 'meal_type', 'entry_type', 'recipe', 'recipe_name', 'servings', 'source')
    list_filter = ('meal_type', 'entry_type', 'source', 'is_ai_suggested')
    inlines = [MealIngredientInline]


@admin.register(MealAnalysis)
class MealAnalysisAdmin(admin.ModelAdmin):
    list_display = ('meal', 'nutrition_strength', 'calories', 'estimated_total_cost_xaf', 'status', 'provider')
    list_filter = ('nutrition_strength', 'status', 'provider', 'is_estimated')
