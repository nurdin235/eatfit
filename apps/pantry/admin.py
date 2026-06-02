from django.contrib import admin

from .models import PantryItem


@admin.register(PantryItem)
class PantryItemAdmin(admin.ModelAdmin):
    # These columns make stock levels easy to inspect from the admin list page.
    list_display = ('household', 'ingredient', 'quantity', 'unit', 'expiry_date', 'low_stock_threshold')
    list_filter = ('ingredient__category',)
    search_fields = ('ingredient__name', 'household__name')
