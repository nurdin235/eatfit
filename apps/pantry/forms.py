from django import forms

from .models import PantryItem


class PantryItemForm(forms.ModelForm):
    """ModelForm for creating and editing pantry stock records."""

    class Meta:
        model = PantryItem
        fields = ['ingredient', 'quantity', 'unit', 'expiry_date', 'low_stock_threshold']
        widgets = {
            'ingredient': forms.Select(attrs={'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'form-input'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'low_stock_threshold': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and (quantity < 0 or quantity > 100000):
            raise forms.ValidationError("Quantity must be from 0 to 100000.")
        return quantity

    def clean_low_stock_threshold(self):
        threshold = self.cleaned_data.get('low_stock_threshold')
        if threshold is not None and (threshold < 0 or threshold > 100000):
            raise forms.ValidationError("Threshold must be from 0 to 100000.")
        return threshold

    def clean_unit(self):
        return (self.cleaned_data.get('unit') or '').strip()[:50]
