from django.contrib import admin

from .models import GroceryItem, GroceryList


class GroceryItemInline(admin.TabularInline):
    # Grocery items are edited inline inside their grocery list.
    model = GroceryItem
    extra = 0


@admin.register(GroceryList)
class GroceryListAdmin(admin.ModelAdmin):
    list_display = ('household', 'meal_plan', 'status', 'total_estimated_cost_xaf', 'created_at')
    list_filter = ('status', 'is_ai_optimized')
    inlines = [GroceryItemInline]


@admin.register(GroceryItem)
class GroceryItemAdmin(admin.ModelAdmin):
    list_display = ('grocery_list', 'ingredient', 'quantity', 'unit', 'is_purchased')
    list_filter = ('is_purchased', 'is_optional')
