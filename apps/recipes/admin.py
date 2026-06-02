from django.contrib import admin

from .models import Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    # Inline rows let admins edit recipe ingredients on the recipe page.
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'cuisine', 'diet_type', 'servings', 'estimated_cost_xaf', 'is_public')
    list_filter = ('cuisine', 'diet_type', 'is_public', 'is_cameroonian')
    search_fields = ('title', 'description')
    inlines = [RecipeIngredientInline]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_unit', 'estimated_cost_per_unit_xaf')
    list_filter = ('category',)
    search_fields = ('name',)
