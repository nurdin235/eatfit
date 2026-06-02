# 06. Forms, Validation, And Data Saving

This document explains how form data moves from the browser into the database in EatFit.

## The Basic Form Saving Flow

Most Django form saving follows this pattern:

```text
1. User fills form in template
2. Browser submits form using POST
3. urls.py maps request to a view
4. View receives request.POST
5. View creates a form object
6. form.is_valid() validates the data
7. form.save() or model.objects.create() saves data
8. Django ORM converts Python objects into SQL
9. Database stores the record
10. User is redirected or shown a success/error page
```

## What `request.POST` Is

When a browser submits an HTML form using:

```html
<form method="post">
```

Django receives the submitted values in:

```python
request.POST
```

Example:

```python
form = MealPlanForm(request.POST)
```

In this project, I did not find active file upload handling with `request.FILES`.

## What `form.is_valid()` Does

`form.is_valid()` checks:

- Required fields
- Field types
- Max lengths
- Min values
- Choice values
- Custom validation methods like `clean_email()` and `clean()`

If the form is valid, cleaned values are stored in:

```python
form.cleaned_data
```

If the form is invalid, errors are shown in templates.

## What `form.save()` Does

For `ModelForm`, `form.save()` creates or updates a database model.

Example:

```python
form.save()
```

This usually writes to the database immediately.

## What `form.save(commit=False)` Does

`commit=False` creates the model object but does not save it yet.

This is useful when the browser should not control some fields.

Example from `apps/meals/views.py`:

```python
meal_plan = form.save(commit=False)
meal_plan.household = household
meal_plan.created_by = request.user
meal_plan.save()
```

The user submits title and dates, but the server attaches the correct household and user.

This is safer because users cannot fake ownership from the browser.

## Registration Form

File:

```text
apps/users/forms.py
```

Form:

```python
CustomUserCreationForm
```

Template:

```text
templates/auth/register.html
```

View:

```text
apps/users/views.py
```

View function:

```python
register_view(request)
```

Fields:

- `username`
- `email`
- `first_name`
- `password1`
- `password2`

Validation:

- Django's `UserCreationForm` checks password confirmation and password rules.
- `clean_email()` checks that the email does not already exist.

Saving:

```python
user = form.save()
user.ensure_household()
Profile.objects.get_or_create(user=user)
login(request, user)
```

What happens internally:

1. User submits form.
2. Django validates username, email, and passwords.
3. Django hashes the password.
4. User is inserted into the users table.
5. A household is created if needed.
6. A profile is created.
7. The user is logged in.

## Login Form

File:

```text
apps/users/forms.py
```

Form:

```python
CustomAuthenticationForm
```

View:

```python
login_view(request)
```

Template:

```text
templates/auth/login.html
```

Validation:

- Checks username and password through Django authentication.

Saving:

Login does not create a new database row. It creates a session.

Important line:

```python
login(request, user)
```

This stores the user's ID in the session so future requests know `request.user`.

## Profile Form

File:

```text
apps/users/forms.py
```

Form:

```python
ProfileForm
```

Template:

```text
templates/users/profile.html
```

View:

```python
profile_view(request)
```

Fields:

- `diet_type`
- `calorie_goal`
- `protein_goal`
- `carbs_goal`
- `fat_goal`
- `weekly_budget_xaf`
- `timezone`
- `measurement_system`
- `allergies_text`
- `likes_text`
- `dislikes_text`

Important detail:

The database stores allergies, likes, and dislikes as JSON lists, but the form accepts comma-separated text.

Example user input:

```text
peanuts, milk, fish
```

The form converts it into:

```python
['peanuts', 'milk', 'fish']
```

Saving:

```python
profile = super().save(commit=False)
profile.allergies = self._split('allergies_text')
profile.likes = self._split('likes_text')
profile.dislikes = self._split('dislikes_text')
profile.save()
profile.user.allergies = profile.allergies
profile.user.dietary_preferences = profile.preference_summary()
profile.user.save(update_fields=['allergies', 'dietary_preferences'])
```

So profile saving also updates selected fields on the user.

## Household Invite Form

File:

```text
apps/users/forms.py
```

Form:

```python
HouseholdInviteForm
```

Template:

```text
templates/users/household.html
```

Fields:

- `username`
- `role`

This is not a `ModelForm`. It is a normal `forms.Form` because it does not directly create a model by itself. The view calls a service:

```python
add_member_by_username(...)
```

Validation:

- Username is required.
- Role must be one of the `HouseholdMembership.Role` choices.

Authorization:

- Only household owners or superusers can submit it successfully.

## Meal Plan Form

File:

```text
apps/meals/forms.py
```

Form:

```python
MealPlanForm
```

Template:

```text
templates/meals/create.html
```

View:

```python
create_meal_plan_view(request)
```

Model:

```python
MealPlan
```

Fields:

- `title`
- `start_date`
- `end_date`
- `weekly_budget_xaf`
- `planning_period`

Important:

`planning_period` is a form-only field. It is not stored directly in the `MealPlan` model.

Choices:

- `single_day`
- `week`
- `custom_range`

Validation in `clean()`:

- If single day, `end_date = start_date`.
- If week, `end_date = start_date + 6 days`.
- If custom range, end date is required.
- End date cannot be before start date.

Saving flow:

```python
form = MealPlanForm(request.POST)
if form.is_valid():
    meal_plan = form.save(commit=False)
    meal_plan.household = household
    meal_plan.created_by = request.user
    meal_plan.save()
```

Database result:

A new `MealPlan` row is created.

## Meal Form

File:

```text
apps/meals/forms.py
```

Form:

```python
MealForm
```

Template:

```text
templates/meals/detail.html
```

View:

```python
meal_plan_detail_view(request, pk)
```

Model:

```python
Meal
```

Fields:

- `entry_type`
- `recipe`
- `recipe_name`
- `date`
- `meal_type`
- `servings`
- `notes`

Validation in `clean()`:

- If `entry_type` is `recipe`, a recipe must be selected.
- If `entry_type` is `custom`, a meal title must be entered.

Additional validation in view:

- Meal date must be inside the plan range.
- Custom meal must include at least one ingredient row.

Saving flow:

```python
meal = form.save(commit=False)
meal.meal_plan = meal_plan
meal.save()
```

If custom:

```python
MealIngredientService.sync_from_form(meal, MealIngredientService.parse_rows(request.POST))
```

Then:

```python
MealAnalysisService().analyze(meal)
ReminderService.schedule(meal)
```

Database result:

- One `Meal` row is created or replaces an existing slot.
- Custom meals create `MealIngredient` rows.
- A `MealAnalysis` row is created or updated.
- Notifications may be created.

## Custom Meal Ingredient Rows

Template:

```text
templates/meals/partials/ingredient_row.html
```

The inputs use repeated names:

```html
ingredient_name[]
ingredient_quantity[]
ingredient_unit[]
ingredient_unit_price_xaf[]
ingredient_id[]
```

Service:

```text
apps/meals/services.py
```

Functions:

```python
MealIngredientService.parse_rows(request.POST)
MealIngredientService.sync_from_form(meal, rows)
```

How it works:

1. `parse_rows()` reads repeated values using `post_data.getlist()`.
2. It combines the values into row dictionaries.
3. `sync_from_form()` deletes old custom ingredient rows for the meal.
4. It creates new `MealIngredient` objects.
5. `MealIngredient.save()` calculates total price.

## Recipe Form

File:

```text
apps/recipes/forms.py
```

Form:

```python
RecipeForm
```

Template:

```text
templates/recipes/form.html
```

View:

```python
_recipe_form(request, recipe=None)
```

Model:

```python
Recipe
```

Fields:

- `title`
- `description`
- `instructions`
- `prep_time`
- `cook_time`
- `servings`
- `diet_type`
- `difficulty`
- `cuisine`
- `is_public`
- `is_cameroonian`
- `allergens_text`
- `tags_text`

Important:

The database stores `allergens` and `tags` as JSON lists. The form accepts comma-separated text.

Saving:

```python
recipe = form.save(commit=False)
recipe.created_by = recipe.created_by or request.user
recipe.household = household
recipe.save()
```

Then recipe ingredient rows are saved through a formset.

## Recipe Ingredient Formset

File:

```text
apps/recipes/forms.py
```

Formset:

```python
RecipeIngredientFormSet
```

Purpose:

Allows many `RecipeIngredient` rows to be edited on the same recipe form page.

Template line:

```django
{{ formset.management_form }}
```

This is required. It tells Django how many ingredient forms were submitted.

Saving:

```python
formset.instance = recipe
formset.save()
NutritionService.calculate_recipe(recipe)
```

Database result:

- `Recipe` row is saved.
- Related `RecipeIngredient` rows are saved.
- Recipe cost and nutrition fields are recalculated.

## Pantry Item Form

File:

```text
apps/pantry/forms.py
```

Form:

```python
PantryItemForm
```

Templates:

```text
templates/pantry/index.html
templates/pantry/form.html
```

Views:

```python
pantry_add_view
pantry_edit_view
pantry_delete_view
```

Fields:

- `ingredient`
- `quantity`
- `unit`
- `expiry_date`
- `low_stock_threshold`

Add saving flow:

```python
item = form.save(commit=False)
item.household = household
item.save()
```

Important:

The household is assigned in the view, not submitted by the browser.

Edit saving flow:

```python
form = PantryItemForm(request.POST, instance=item)
form.save()
```

Delete flow:

```python
item.delete()
```

## Grocery Item Form

File:

```text
apps/groceries/forms.py
```

Form:

```python
GroceryItemForm
```

Template:

```text
templates/groceries/item_form.html
```

View:

```python
grocery_item_update_view(request, pk, item_pk)
```

Fields:

- `quantity`
- `unit`
- `is_purchased`
- `is_optional`

Saving:

```python
updated = form.save(commit=False)
updated.manually_adjusted = True
updated.save()
```

Database result:

The item is updated and marked as manually adjusted.

## Notification Preference Form

File:

```text
apps/notifications/forms.py
```

Form:

```python
NotificationPreferenceForm
```

Template:

```text
templates/notifications/index.html
```

View:

```python
notifications_view(request)
```

Fields:

- `meal_reminders_enabled`
- `breakfast_time`
- `lunch_time`
- `dinner_time`
- `reminder_minutes_before`

Saving:

```python
form = NotificationPreferenceForm(request.POST, instance=prefs)
form.save()
```

Database result:

The user's notification preference row is updated.

## Database Saving Without Forms

Some parts of EatFit save directly with model methods or services.

### Create Household

File:

```text
apps/users/models.py
```

Code:

```python
Household.objects.create(name=f"{self.username}'s Household")
```

### Create Grocery List

File:

```text
apps/groceries/services.py
```

Code:

```python
GroceryList.objects.create(...)
GroceryItem.objects.create(...)
```

### Update Or Create Analysis

File:

```text
apps/meals/services.py
```

Code:

```python
MealAnalysis.objects.update_or_create(...)
```

This updates the old analysis if it exists, or creates a new one if it does not.

### Create Notification

File:

```text
apps/notifications/services.py
```

Code:

```python
Notification.objects.get_or_create(...)
```

This avoids creating duplicate reminders for the same user, type, title, and scheduled time.

## GET Forms Versus POST Forms

### GET Form Example

Recipe search uses GET.

Template:

```text
templates/recipes/index.html
```

Input:

```html
<form method="get">
```

View:

```python
query = request.GET.get('q', '').strip()
```

GET is good for search because it does not change the database.

### POST Form Example

Creating a meal plan uses POST.

Template:

```text
templates/meals/create.html
```

Input:

```html
<form method="POST">
```

View:

```python
form = MealPlanForm(request.POST)
```

POST is used because it changes the database.

## CSRF In Forms

Every important POST form includes:

```django
{% csrf_token %}
```

Examples:

- `templates/auth/register.html`
- `templates/auth/login.html`
- `templates/meals/create.html`
- `templates/meals/detail.html`
- `templates/recipes/form.html`
- `templates/pantry/form.html`
- `templates/groceries/item_form.html`
- `templates/notifications/index.html`

This token is checked by:

```python
'django.middleware.csrf.CsrfViewMiddleware'
```

in `config/settings.py`.

## Full Example: From Browser To Database

Feature:

Create a custom meal inside a meal plan.

Files:

- `templates/meals/detail.html`
- `templates/meals/partials/ingredient_row.html`
- `apps/meals/urls.py`
- `apps/meals/views.py`
- `apps/meals/forms.py`
- `apps/meals/services.py`
- `apps/meals/models.py`

Step-by-step:

1. User opens a meal plan detail page.
2. User selects "Custom meal".
3. User enters:
   - meal title
   - date
   - meal type
   - servings
   - notes
   - ingredient rows
4. Browser sends POST to `/meal-plans/<id>/`.
5. `apps/meals/urls.py` routes to `meal_plan_detail_view`.
6. The view creates:

```python
form = MealForm(request.POST)
```

7. `form.is_valid()` checks the normal meal fields.
8. The view checks that the date is inside the meal plan range.
9. The view checks there is at least one custom ingredient.
10. Existing meal in the same slot is deleted.
11. The view creates the meal:

```python
meal = form.save(commit=False)
meal.meal_plan = meal_plan
meal.recipe = None
meal.recipe_name = form.cleaned_data['recipe_name'].strip()
meal.save()
```

12. Custom ingredient rows are parsed:

```python
MealIngredientService.parse_rows(request.POST)
```

13. Ingredient rows are saved:

```python
MealIngredientService.sync_from_form(meal, rows)
```

14. Meal analysis is saved:

```python
MealAnalysisService().analyze(meal)
```

15. Reminder notifications may be created:

```python
ReminderService.schedule(meal)
```

16. Django redirects back to the meal plan detail page.

## Common Beginner Mistakes

### Forgetting `{% csrf_token %}`

Problem:

POST form returns 403 Forbidden.

Fix:

Add:

```django
{% csrf_token %}
```

inside the form.

### Forgetting `commit=False`

Problem:

You need to attach `request.user` or `household`, but the object saved too early.

Fix:

Use:

```python
obj = form.save(commit=False)
obj.user = request.user
obj.save()
```

### Not Passing `instance`

Problem:

Editing creates a new row instead of updating the old row.

Fix:

Use:

```python
form = SomeForm(request.POST, instance=existing_object)
```

### Not Redirecting After POST

Problem:

Refreshing the page resubmits the form.

Fix:

Use:

```python
return redirect(...)
```

after a successful POST.

EatFit follows this pattern in most views.
