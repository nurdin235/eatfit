from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Household, HouseholdMembership, Profile, User


@admin.register(User)
class EatFitUserAdmin(UserAdmin):
    # list_display controls the columns shown in Django admin.
    list_display = ('username', 'email', 'household', 'is_staff', 'is_active')
    search_fields = ('username', 'email')


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    # search_fields lets staff quickly find a household by name or invite code.
    list_display = ('name', 'invite_code', 'created_at')
    search_fields = ('name', 'invite_code')


@admin.register(HouseholdMembership)
class HouseholdMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'household', 'role', 'joined_at')
    list_filter = ('role',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'diet_type', 'weekly_budget_xaf', 'timezone')
    search_fields = ('user__username', 'user__email')
