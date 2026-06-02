from django import forms

from .models import GroceryItem


class GroceryItemForm(forms.ModelForm):
    """Lets users adjust generated grocery item quantities and purchase state."""

    class Meta:
        model = GroceryItem
        fields = ['quantity', 'unit', 'is_purchased', 'is_optional']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'unit': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and (quantity < 0 or quantity > 100000):
            raise forms.ValidationError("Quantity must be from 0 to 100000.")
        return quantity

    def clean_unit(self):
        return (self.cleaned_data.get('unit') or '').strip()[:50]
