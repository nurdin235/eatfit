from datetime import timedelta

from django import forms
from .models import MealPlan, Meal
from apps.recipes.models import Recipe

class MealPlanForm(forms.ModelForm):
    """Creates a plan and can auto-calculate the end date from the chosen period."""

    PLANNING_PERIODS = (
        ('single_day', 'Single day'),
        ('week', 'One week'),
        ('custom_range', 'Custom range'),
    )
    planning_period = forms.ChoiceField(
        choices=PLANNING_PERIODS,
        initial='week',
        widget=forms.Select(attrs={'class': 'form-input'}),
    )

    class Meta:
        model = MealPlan
        fields = ['title', 'start_date', 'end_date', 'weekly_budget_xaf']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'weekly_budget_xaf': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['end_date'].required = False

    def clean(self):
        # clean() validates fields together, so start_date can affect end_date.
        cleaned = super().clean()
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')
        planning_period = self.cleaned_data.get('planning_period')
        if start and planning_period == 'single_day':
            cleaned['end_date'] = start
            return cleaned
        if start and planning_period == 'week':
            cleaned['end_date'] = start + timedelta(days=6)
            return cleaned
        if planning_period == 'custom_range' and not end:
            self.add_error('end_date', "End date is required for a custom range.")
        if start and end and end < start:
            raise forms.ValidationError("End date must be after start date.")
        if start and cleaned.get('end_date') and (cleaned['end_date'] - start).days > 31:
            raise forms.ValidationError("Meal plans can cover at most 31 days.")
        return cleaned

class MealForm(forms.ModelForm):
    """Adds or replaces one meal slot inside an existing MealPlan."""

    class Meta:
        model = Meal
        fields = ['entry_type', 'recipe', 'recipe_name', 'date', 'meal_type', 'servings', 'notes']
        widgets = {
            'entry_type': forms.Select(attrs={'class': 'form-input'}),
            'recipe': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'recipe_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Fried plantain and eggs'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'meal_type': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'servings': forms.NumberInput(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipe'].required = False
        self.fields['recipe_name'].required = False

    def clean(self):
        # A meal must be either a selected recipe or a titled custom meal.
        cleaned = super().clean()
        entry_type = cleaned.get('entry_type')
        recipe = cleaned.get('recipe')
        recipe_name = (cleaned.get('recipe_name') or '').strip()
        if entry_type == 'recipe' and not recipe:
            self.add_error('recipe', "Choose an existing recipe or switch to custom meal.")
        if entry_type == 'custom' and not recipe_name:
            self.add_error('recipe_name', "Give this custom meal a title.")
        return cleaned

    def clean_recipe_name(self):
        return (self.cleaned_data.get('recipe_name') or '').strip()[:255]

    def clean_notes(self):
        notes = (self.cleaned_data.get('notes') or '').strip()
        if len(notes) > 1200:
            raise forms.ValidationError("Keep notes under 1200 characters.")
        return notes

    def clean_servings(self):
        servings = self.cleaned_data.get('servings')
        if servings is None:
            return servings
        if servings < 1 or servings > 100:
            raise forms.ValidationError("Servings must be from 1 to 100.")
        return servings
