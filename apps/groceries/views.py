from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.services import assert_household_editor, get_active_household

from .forms import GroceryItemForm
from .models import GroceryItem, GroceryList

@login_required
def groceries_view(request):
    """List grocery lists for the active household."""

    household = get_active_household(request.user)
    lists = GroceryList.objects.filter(household=household).prefetch_related('items__ingredient')
    return render(request, 'groceries/index.html', {'lists': lists})


@login_required
def grocery_detail_view(request, pk):
    household = get_active_household(request.user)
    grocery_list = get_object_or_404(GroceryList.objects.prefetch_related('items__ingredient'), pk=pk, household=household)
    return render(request, 'groceries/detail.html', {'grocery_list': grocery_list})


@login_required
def grocery_item_update_view(request, pk, item_pk):
    """Allow a user to manually adjust one generated grocery item."""

    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    grocery_list = get_object_or_404(GroceryList, pk=pk, household=household)
    item = get_object_or_404(GroceryItem, pk=item_pk, grocery_list=grocery_list)
    if request.method == 'POST':
        form = GroceryItemForm(request.POST, instance=item)
        if form.is_valid():
            updated = form.save(commit=False)
            # This flag records that the generated line was changed by a human.
            updated.manually_adjusted = True
            updated.save()
            messages.success(request, "Grocery item updated.")
            return redirect('groceries:detail', pk=pk)
    else:
        form = GroceryItemForm(instance=item)
    return render(request, 'groceries/item_form.html', {'form': form, 'grocery_list': grocery_list, 'item': item})


@login_required
def grocery_item_toggle_view(request, pk, item_pk):
    household = get_active_household(request.user)
    assert_household_editor(request.user, household)
    grocery_list = get_object_or_404(GroceryList, pk=pk, household=household)
    item = get_object_or_404(GroceryItem, pk=item_pk, grocery_list=grocery_list)
    if request.method == 'POST':
        item.is_purchased = not item.is_purchased
        item.save(update_fields=['is_purchased'])
    return redirect('groceries:detail', pk=pk)
