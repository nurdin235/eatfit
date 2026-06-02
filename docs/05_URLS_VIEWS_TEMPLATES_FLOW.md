# 05. URLs, Views, Templates Flow

This document explains how a browser request moves through EatFit.

## Main Flow

The basic flow is:

```text
Browser/User
-> URL
-> config/urls.py
-> app urls.py
-> view function
-> form validation if needed
-> model/database operation if needed
-> template rendering or redirect
-> response displayed to user
```

## Project URL File

File:

```text
config/urls.py
```

This is the first URL file Django reads.

Important page routes:

```text
/admin/
/
/auth/
/profile/
/households/
/meal-plans/
/groceries/
/pantry/
/recipes/
/nutrition/
/budget/
/notifications/
```

Important API routes:

```text
/api/v1/auth/token/
/api/v1/auth/token/refresh/
/api/v1/users/
/api/v1/meal-plans/
/api/v1/recipes/
/api/v1/grocery-lists/
/api/v1/notifications/
/api/v1/ai/
```

## Dashboard Flow

URL:

```text
/
```

Files involved:

- `config/urls.py`
- `apps/core/urls.py`
- `apps/core/views.py`
- `templates/dashboard/dashboard.html`

View:

```python
dashboard(request)
```

Step-by-step:

1. Browser requests `/`.
2. `config/urls.py` includes `apps.core.urls`.
3. `apps/core/urls.py` maps `''` to `dashboard`.
4. `@login_required` checks that the user is logged in.
5. `get_active_household(request.user)` finds or creates the user's household.
6. The view loads:
   - latest meal plan
   - upcoming meals
   - nutrition totals
   - latest grocery list
   - unread notification count
   - low stock pantry count
   - total meal count
7. The view renders `templates/dashboard/dashboard.html`.
8. The browser displays the dashboard.

Security:

- Anonymous users are redirected to `/auth/login/`.
- Data is filtered by the active household.

## Registration Flow

URL:

```text
/auth/register/
```

Files involved:

- `config/urls.py`
- `apps/users/auth_urls.py`
- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/models.py`
- `apps/users/signals.py`
- `templates/auth/register.html`

View:

```python
register_view(request)
```

Form:

```python
CustomUserCreationForm
```

Step-by-step:

1. Browser opens `/auth/register/` using GET.
2. The view displays a blank `CustomUserCreationForm`.
3. User fills username, email, first name, password, and confirmation.
4. Browser submits POST data.
5. The view creates:

```python
form = CustomUserCreationForm(request.POST)
```

6. `form.is_valid()` checks password rules and unique email.
7. `form.save()` creates the `User`.
8. Django hashes the password before storing it.
9. `user.ensure_household()` creates a household and owner membership if needed.
10. `Profile.objects.get_or_create(user=user)` makes sure the profile exists.
11. `login(request, user)` starts the session.
12. User is redirected to the dashboard.

Template:

```text
templates/auth/register.html
```

Security:

- Passwords are hashed by Django.
- CSRF token is included.
- Duplicate emails are rejected in `clean_email()`.

## Login Flow

URL:

```text
/auth/login/
```

Files involved:

- `apps/users/auth_urls.py`
- `apps/users/views.py`
- `apps/users/forms.py`
- `templates/auth/login.html`

View:

```python
login_view(request)
```

Form:

```python
CustomAuthenticationForm
```

Step-by-step:

1. Browser opens `/auth/login/` using GET.
2. The view displays the login form.
3. User submits username and password using POST.
4. The view creates:

```python
form = CustomAuthenticationForm(request, data=request.POST)
```

5. `form.is_valid()` checks credentials.
6. The view calls:

```python
authenticate(username=username, password=password)
```

7. If valid, `login(request, user)` stores the user's ID in the session.
8. User is redirected to dashboard.

Security:

- Django checks the password against the stored hash.
- CSRF token is included.
- Session middleware remembers the logged-in user.

## Logout Flow

URL:

```text
/auth/logout/
```

Files involved:

- `apps/users/auth_urls.py`
- `apps/users/views.py`
- `templates/partials/navbar.html`

View:

```python
logout_view(request)
```

Step-by-step:

1. User clicks "Sign out" in the navbar.
2. Browser requests `/auth/logout/`.
3. The view calls:

```python
logout(request)
```

4. Django clears the session.
5. User is redirected to login page.

Best-practice note:

Currently logout is linked with a normal anchor tag. For stronger CSRF protection, logout is often implemented as a POST-only form. This is documented in the security guide.

## Profile Flow

URL:

```text
/profile/
```

Files involved:

- `config/urls.py`
- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/models.py`
- `templates/users/profile.html`

View:

```python
profile_view(request)
```

Form:

```python
ProfileForm
```

Step-by-step:

1. User opens `/profile/`.
2. `@login_required` checks login.
3. The view gets or creates `Profile`.
4. On GET, the form is filled with profile data.
5. On POST, `ProfileForm(request.POST, instance=profile)` validates input.
6. `ProfileForm.save()` converts comma-separated allergies, likes, and dislikes into JSON lists.
7. The profile is saved.
8. The linked `User` allergy and preference fields are updated.
9. User is redirected back to profile.

Template:

```text
templates/users/profile.html
```

Security:

- A user can edit only their own profile because the view uses `request.user`.

## Household Flow

URL:

```text
/households/
```

Files involved:

- `config/urls.py`
- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/services.py`
- `templates/users/household.html`

View:

```python
household_view(request)
```

Step-by-step:

1. User opens `/households/`.
2. The view gets the active household.
3. The view gets the user's role with `user_role()`.
4. The page shows household members.
5. On POST, only owners and superusers can add members.
6. The form accepts username and role.
7. `add_member_by_username()` creates or updates `HouseholdMembership`.
8. User is redirected back to household page.

Security:

- Non-owners cannot add members.
- Membership is unique per user and household.

## Recipe List And Search Flow

URL:

```text
/recipes/
```

Files involved:

- `apps/recipes/urls.py`
- `apps/recipes/views.py`
- `templates/recipes/index.html`

View:

```python
recipes_view(request)
```

Step-by-step:

1. User opens `/recipes/`.
2. The view gets the active household.
3. It loads public recipes and household recipes.
4. If `q` exists in the GET query string, it filters by title, description, cuisine, or diet type.
5. The view renders `templates/recipes/index.html`.

Search example:

```text
/recipes/?q=rice
```

Security:

- Private recipes are shown only to their household.
- Search uses Django ORM filters, not raw SQL.

## Recipe Create/Edit Flow

URLs:

```text
/recipes/new/
/recipes/<id>/edit/
```

Files involved:

- `apps/recipes/views.py`
- `apps/recipes/forms.py`
- `apps/recipes/models.py`
- `templates/recipes/form.html`

Views:

```python
recipe_create_view(request)
recipe_edit_view(request, pk)
_recipe_form(request, recipe=None)
```

Forms:

```python
RecipeForm
RecipeIngredientFormSet
```

Step-by-step:

1. User opens create or edit page.
2. View displays recipe form and ingredient formset.
3. User submits POST data.
4. `RecipeForm` validates recipe fields.
5. `RecipeIngredientFormSet` validates ingredient rows.
6. `form.save(commit=False)` creates a recipe object without final save.
7. The view sets `created_by` and `household`.
8. `recipe.save()` writes the recipe.
9. `formset.instance = recipe` connects ingredient rows to the recipe.
10. `formset.save()` writes recipe ingredients.
11. `NutritionService.calculate_recipe(recipe)` updates recipe nutrition and cost.
12. User is redirected to recipe detail.

Security:

- Edit and delete only load recipes where `household=active_household`.
- CSRF token protects POST forms.

## Recipe Delete Flow

URL:

```text
/recipes/<id>/delete/
```

View:

```python
recipe_delete_view(request, pk)
```

Template:

```text
templates/recipes/confirm_delete.html
```

Step-by-step:

1. User opens delete confirmation page.
2. View loads recipe by ID and household.
3. User submits POST confirmation.
4. `recipe.delete()` removes the row.
5. User is redirected to recipe list.

## Meal Plan Create Flow

URL:

```text
/meal-plans/create/
```

Files involved:

- `apps/meals/urls.py`
- `apps/meals/views.py`
- `apps/meals/forms.py`
- `templates/meals/create.html`

View:

```python
create_meal_plan_view(request)
```

Form:

```python
MealPlanForm
```

Step-by-step:

1. User opens create page.
2. The view displays `MealPlanForm`.
3. User chooses title, planning period, start date, optional end date, and budget.
4. The browser submits POST.
5. `MealPlanForm.clean()` calculates `end_date` for single day or week.
6. The view calls `form.save(commit=False)`.
7. The view attaches:

```python
meal_plan.household = household
meal_plan.created_by = request.user
```

8. `meal_plan.save()` writes the database row.
9. User is redirected to meal plan detail.

Security:

- `assert_household_editor()` checks the user can edit household data.

## Meal Plan Detail And Add Meal Flow

URL:

```text
/meal-plans/<id>/
```

Files involved:

- `apps/meals/views.py`
- `apps/meals/forms.py`
- `apps/meals/services.py`
- `apps/notifications/services.py`
- `apps/nutrition/services.py`
- `apps/ai_services/services.py`
- `templates/meals/detail.html`
- `templates/meals/partials/ingredient_row.html`

View:

```python
meal_plan_detail_view(request, pk)
```

Form:

```python
MealForm
```

Step-by-step on GET:

1. View loads the meal plan for the active household.
2. View loads existing meals.
3. View builds planner days from start date to end date.
4. View loads recipes available to the household.
5. View calculates nutrition and budget summaries.
6. View gets AI or fallback recommendations.
7. Template displays planner grid and add-meal form.

Step-by-step on POST:

1. User submits add/replace meal form.
2. View creates `MealForm(request.POST)`.
3. The recipe field queryset is limited to allowed recipes.
4. `form.is_valid()` checks recipe/custom meal requirements.
5. The view checks meal date is inside the plan range.
6. If custom meal, it checks that at least one ingredient row was entered.
7. Existing meal in the same date/type slot is deleted.
8. `form.save(commit=False)` creates a meal object.
9. The view attaches the meal plan.
10. If custom, it saves `recipe_name` and clears `recipe`.
11. `meal.save()` writes the meal.
12. For custom meals, `MealIngredientService.sync_from_form()` saves ingredient rows.
13. `MealAnalysisService().analyze(meal)` stores nutrition analysis.
14. `ReminderService.schedule(meal)` creates reminders.
15. User is redirected back to the detail page.

Security:

- Meal plan is loaded with `pk=pk, household=household`.
- Editing requires editor role.
- CSRF token protects POST.

## Delete Meal Flow

URL:

```text
/meal-plans/<plan_id>/meals/<meal_id>/delete/
```

View:

```python
delete_meal_view(request, pk, meal_pk)
```

Step-by-step:

1. View loads meal plan by household.
2. View loads meal inside that plan.
3. On POST, editor permission is checked.
4. `meal.delete()` removes the meal.
5. User is redirected back to meal plan detail.

## Analyze Meal Flow

URL:

```text
/meal-plans/<plan_id>/meals/<meal_id>/analyze/
```

View:

```python
analyze_meal_view(request, pk, meal_pk)
```

Step-by-step:

1. View loads meal plan and meal by household.
2. On POST, editor permission is checked.
3. `MealAnalysisService().analyze(meal)` recalculates analysis.
4. User is redirected back to detail page.

## Generate Grocery List Flow

URL:

```text
/meal-plans/<id>/grocery-list/
```

View:

```python
generate_grocery_list_view(request, pk)
```

Service:

```python
GroceryGenerationService.generate(meal_plan, request.user)
```

Step-by-step:

1. User clicks "Generate grocery list".
2. Browser sends POST.
3. View loads meal plan by household.
4. Editor permission is checked.
5. Grocery service creates a `GroceryList`.
6. Service reads recipe ingredients and custom meal ingredients.
7. Service subtracts matching pantry stock.
8. Service creates `GroceryItem` rows.
9. Service updates `total_estimated_cost_xaf`.
10. Budget service evaluates cost against budget.
11. User is redirected to grocery list detail.

## Grocery List Flow

URLs:

```text
/groceries/
/groceries/<id>/
/groceries/<id>/items/<item_id>/edit/
/groceries/<id>/items/<item_id>/toggle/
```

Files involved:

- `apps/groceries/views.py`
- `apps/groceries/forms.py`
- `templates/groceries/index.html`
- `templates/groceries/detail.html`
- `templates/groceries/item_form.html`

Important views:

- `groceries_view`
- `grocery_detail_view`
- `grocery_item_update_view`
- `grocery_item_toggle_view`

Security:

- Grocery lists are always loaded by active household.
- Item edits are loaded through the selected grocery list.

## Pantry CRUD Flow

URLs:

```text
/pantry/
/pantry/add/
/pantry/<id>/edit/
/pantry/<id>/delete/
```

Files involved:

- `apps/pantry/views.py`
- `apps/pantry/forms.py`
- `templates/pantry/index.html`
- `templates/pantry/form.html`

Views:

- `pantry_view`
- `pantry_add_view`
- `pantry_edit_view`
- `pantry_delete_view`

Step-by-step add:

1. User opens `/pantry/add/`.
2. View shows `PantryItemForm`.
3. User submits POST.
4. `form.is_valid()` validates ingredient, quantity, unit, expiry date, and threshold.
5. `form.save(commit=False)` creates object without saving.
6. View sets `item.household = household`.
7. `item.save()` writes to database.
8. User is redirected to pantry list.

Security:

- The browser does not choose the household. The server sets it.
- Edit and delete filter by active household.

## Nutrition Flow

URLs:

```text
/nutrition/
/budget/
/nutrition/budget/
```

Files involved:

- `apps/nutrition/views.py`
- `apps/nutrition/services.py`
- `templates/nutrition/index.html`
- `templates/nutrition/budget.html`

Views:

- `nutrition_view`
- `budget_view`

Step-by-step:

1. User opens nutrition or budget page.
2. View gets active household.
3. View loads latest or recent meal plans.
4. `NutritionService` calculates totals.
5. `BudgetService` compares grocery totals with budget.
6. Template displays read-only summary.

## Notifications Flow

URLs:

```text
/notifications/
/notifications/<id>/read/
```

Files involved:

- `apps/notifications/views.py`
- `apps/notifications/forms.py`
- `apps/notifications/services.py`
- `templates/notifications/index.html`

Views:

- `notifications_view`
- `notification_mark_read_view`

Step-by-step:

1. User opens `/notifications/`.
2. View loads `request.user.notifications.all()`.
3. View gets or creates `NotificationPreference`.
4. If POST on settings form, preferences are saved.
5. If POST to mark read, one notification is marked read.

Security:

- Notification read route uses `pk=pk, user=request.user`.
- Users cannot mark another user's notification as read.

## API Flow

API routes use Django REST Framework.

Authentication:

- Session authentication
- JWT authentication

Permissions:

```python
IsAuthenticated
```

Example API:

```text
GET /api/v1/recipes/
```

Flow:

1. API client sends request.
2. DRF authenticates the user.
3. `recipe_list()` gets active household.
4. It queries public and household recipes.
5. `RecipeSerializer` converts models to JSON.
6. DRF returns JSON response.

## Template Inheritance Flow

Most templates start with:

```django
{% extends "base/base.html" %}
```

That means they reuse:

```text
templates/base/base.html
```

The base template includes:

- `templates/partials/navbar.html`
- `templates/partials/sidebar.html`
- `templates/partials/alerts.html`
- `templates/partials/footer.html`

Then each page fills:

```django
{% block content %}
...
{% endblock %}
```

This keeps the UI consistent across pages.
