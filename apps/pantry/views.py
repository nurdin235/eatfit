from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.services import assert_household_editor, get_active_household

from .forms import PantryItemForm
from .models import PantryItem

@login_required
def pantry_view(request):
    """Show pantry items that belong to the active household."""

    household = get_active_household(request.user)
    items = PantryItem.objects.filter(household=household).select_related('ingredient')
    form = PantryItemForm()
    return render(request, 'pantry/index.html', {'items': items, 'form': form})


@login_required
def pantry_add_view(request):
    """Save a new PantryItem after attaching the current household."""

    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    if request.method == 'POST':
        form = PantryItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            # The browser does not choose household; the server sets it securely.
            item.household = household
            item.save()
            messages.success(request, "Pantry item saved.")
            return redirect('pantry:index')
    return render(request, 'pantry/form.html', {'form': form})


@login_required
def pantry_edit_view(request, pk):
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    item = get_object_or_404(PantryItem, pk=pk, household=household)
    if request.method == 'POST':
        form = PantryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Pantry item updated.")
            return redirect('pantry:index')
    else:
        form = PantryItemForm(instance=item)
    return render(request, 'pantry/form.html', {'form': form, 'item': item})


@login_required
def pantry_delete_view(request, pk):
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    item = get_object_or_404(PantryItem, pk=pk, household=household)
    if request.method == 'POST':
        item.delete()
        messages.success(request, "Pantry item removed.")
    return redirect('pantry:index')
