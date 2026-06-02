from django.db import models
from django.contrib.auth.models import AbstractUser

class Household(models.Model):
    """A shared space where family members manage meals, pantry, and groceries."""

    name = models.CharField(max_length=255)
    invite_code = models.CharField(max_length=32, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.invite_code:
            from secrets import token_urlsafe
            # The invite code is created automatically the first time a household is saved.
            self.invite_code = token_urlsafe(12)
        super().save(*args, **kwargs)

class User(AbstractUser):
    """Custom user model so EatFit can store household and diet data on users."""

    household = models.ForeignKey(Household, null=True, blank=True, on_delete=models.SET_NULL, related_name='members')
    dietary_preferences = models.JSONField(default=dict, blank=True)
    allergies = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return self.username

    @property
    def active_household(self):
        # Prefer the direct household field, then fall back to membership records.
        if self.household_id:
            return self.household
        membership = self.household_memberships.select_related('household').first()
        return membership.household if membership else None

    def ensure_household(self):
        # New users need a household so all later queries can safely filter by it.
        household = self.active_household
        if household:
            return household
        household = Household.objects.create(name=f"{self.username}'s Household")
        HouseholdMembership.objects.create(user=self, household=household, role=HouseholdMembership.Role.OWNER)
        self.household = household
        self.save(update_fields=['household'])
        return household


class HouseholdMembership(models.Model):
    """Connects a user to a household and stores their permission role."""

    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        EDITOR = 'editor', 'Editor'
        VIEWER = 'viewer', 'Viewer'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='household_memberships')
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.EDITOR)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'household'], name='unique_household_membership'),
        ]

    def __str__(self):
        return f"{self.user} in {self.household} ({self.role})"


class Profile(models.Model):
    """Nutrition goals and preferences used by recipe filtering and AI ranking."""

    class DietType(models.TextChoices):
        NONE = 'none', 'No restriction'
        VEGETARIAN = 'vegetarian', 'Vegetarian'
        VEGAN = 'vegan', 'Vegan'
        KETO = 'keto', 'Keto'
        HIGH_PROTEIN = 'high_protein', 'High protein'
        LOW_CARB = 'low_carb', 'Low carb'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    diet_type = models.CharField(max_length=30, choices=DietType.choices, default=DietType.NONE)
    allergies = models.JSONField(default=list, blank=True)
    likes = models.JSONField(default=list, blank=True)
    dislikes = models.JSONField(default=list, blank=True)
    calorie_goal = models.PositiveIntegerField(default=2200)
    protein_goal = models.PositiveIntegerField(default=100)
    carbs_goal = models.PositiveIntegerField(default=250)
    fat_goal = models.PositiveIntegerField(default=70)
    weekly_budget_xaf = models.PositiveIntegerField(default=35000)
    timezone = models.CharField(max_length=64, default='Africa/Douala')
    measurement_system = models.CharField(max_length=20, default='metric')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} profile"

    def preference_summary(self):
        # Services use this compact dictionary instead of reading many fields manually.
        return {
            'diet_type': self.diet_type,
            'allergies': self.allergies,
            'likes': self.likes,
            'dislikes': self.dislikes,
            'weekly_budget_xaf': self.weekly_budget_xaf,
        }
