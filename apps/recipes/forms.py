from django import forms
from django.forms import inlineformset_factory

from .models import Recipe, RecipeIngredient


class RecipeForm(forms.ModelForm):
    """Recipe form with extra text fields for list-like JSON data."""

    allergens_text = forms.CharField(required=False, help_text='Separate values with commas')
    tags_text = forms.CharField(required=False, help_text='Separate values with commas')

    class Meta:
        model = Recipe
        fields = [
            'title',
            'description',
            'instructions',
            'prep_time',
            'cook_time',
            'servings',
            'diet_type',
            'difficulty',
            'cuisine',
            'is_public',
            'is_cameroonian',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['allergens_text'].initial = ', '.join(self.instance.allergens)
            self.fields['tags_text'].initial = ', '.join(self.instance.tags)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-input')

    def save(self, commit=True):
        # commit=False lets the view add created_by and household before final save.
        recipe = super().save(commit=False)
        recipe.allergens = self._split('allergens_text')
        recipe.tags = self._split('tags_text')
        if commit:
            recipe.save()
        return recipe

    def clean_description(self):
        return self._clean_limited_text('description', 1200)

    def clean_instructions(self):
        return self._clean_limited_text('instructions', 5000)

    def clean_prep_time(self):
        return self._clean_positive_int('prep_time', 0, 1440)

    def clean_cook_time(self):
        return self._clean_positive_int('cook_time', 0, 1440)

    def clean_servings(self):
        return self._clean_positive_int('servings', 1, 100)

    def _clean_limited_text(self, field_name, max_length):
        value = self.cleaned_data.get(field_name, '').strip()
        if len(value) > max_length:
            raise forms.ValidationError(f"Keep this under {max_length} characters.")
        return value

    def _clean_positive_int(self, field_name, minimum, maximum):
        value = self.cleaned_data.get(field_name)
        if value is None:
            return value
        if value < minimum or value > maximum:
            raise forms.ValidationError(f"Enter a value from {minimum} to {maximum}.")
        return value

    def _split(self, field_name):
        value = self.cleaned_data.get(field_name, '')
        items = [item.strip().lower()[:80] for item in value.split(',') if item.strip()]
        return items[:30]


RecipeIngredientFormSet = inlineformset_factory(
    # The formset edits many RecipeIngredient rows on the same recipe form page.
    Recipe,
    RecipeIngredient,
    fields=('ingredient', 'quantity', 'unit'),
    extra=3,
    can_delete=True,
    widgets={
        'ingredient': forms.Select(attrs={'class': 'form-input'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        'unit': forms.TextInput(attrs={'class': 'form-input'}),
    },
)
