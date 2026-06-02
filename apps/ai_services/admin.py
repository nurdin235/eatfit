from django.contrib import admin

from .models import AIInteractionLog


@admin.register(AIInteractionLog)
class AIInteractionLogAdmin(admin.ModelAdmin):
    # Logs are searchable for auditing AI usage without exposing raw prompts.
    list_display = ('user', 'operation', 'provider', 'model', 'status', 'created_at')
    list_filter = ('provider', 'status', 'operation')
    search_fields = ('user__username', 'operation', 'output_summary')
