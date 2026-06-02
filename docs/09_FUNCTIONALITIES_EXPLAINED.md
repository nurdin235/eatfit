# 09. Functionalities Explained

This document lists the main functionality implemented in EatFit and explains how each one works.

## User Registration

- Purpose: Create a new user account.
- User action: Fill the registration form and submit.
- Files involved: `apps/users/views.py`, `apps/users/forms.py`, `apps/users/models.py`, `templates/auth/register.html`, `apps/users/auth_urls.py`.
- URL involved: `/auth/register/`
- View involved: `register_view`
- Template involved: `templates/auth/register.html`
- Model/database involved: `User`, `Household`, `HouseholdMembership`, `Profile`
- Step-by-step flow: User submits POST. `CustomUserCreationForm` validates input. `form.save()` creates the user. `ensure_household()` creates a household and owner membership. Profile is created. User is logged in and redirected to dashboard.
- Security consideration: Password hashing is handled by Django. Duplicate email is blocked. CSRF token protects the form.
- How to explain it during presentation/viva: "Registration uses Django's `UserCreationForm`, then the system automatically creates a household and profile so the new user can immediately use the meal planner."

## User Login

- Purpose: Authenticate an existing user.
- User action: Enter username and password.
- Files involved: `apps/users/views.py`, `apps/users/forms.py`, `templates/auth/login.html`, `apps/users/auth_urls.py`.
- URL involved: `/auth/login/`
- View involved: `login_view`
- Template involved: `templates/auth/login.html`
- Model/database involved: `User`, session table
- Step-by-step flow: User submits POST. `CustomAuthenticationForm` validates credentials. `authenticate()` checks username/password. `login()` stores the user in the session. User is redirected to dashboard.
- Security consideration: Password is checked against a hash. CSRF token is present. Session cookie stores login state.
- How to explain it during presentation/viva: "Login does not store a password again. It checks the password and creates a session so Django remembers the user."

## User Logout

- Purpose: End the user's session.
- User action: Click "Sign out".
- Files involved: `apps/users/views.py`, `apps/users/auth_urls.py`, `templates/partials/navbar.html`.
- URL involved: `/auth/logout/`
- View involved: `logout_view`
- Template involved: `templates/partials/navbar.html`
- Model/database involved: Django session
- Step-by-step flow: User opens logout URL. `logout(request)` clears the session. User is redirected to login.
- Security consideration: Current logout is GET-based. A POST-based logout form would be stronger.
- How to explain it during presentation/viva: "Logout clears the session, so Django no longer treats the browser as authenticated."

## Dashboard

- Purpose: Show a summary of the user's household planning state.
- User action: Visit the home page after login.
- Files involved: `apps/core/views.py`, `apps/core/urls.py`, `templates/dashboard/dashboard.html`.
- URL involved: `/`
- View involved: `dashboard`
- Template involved: `templates/dashboard/dashboard.html`
- Model/database involved: `MealPlan`, `Meal`, `GroceryList`, `PantryItem`, `Notification`
- Step-by-step flow: View gets active household, latest meal plan, meals, nutrition totals, latest grocery list, low stock count, unread notifications, and meal count. Template displays summary cards.
- Security consideration: `@login_required` protects the dashboard. Queries are filtered by household.
- How to explain it during presentation/viva: "The dashboard is not a separate database table. It collects summary information from several models and displays it in one page."

## Profile Management

- Purpose: Store diet preferences, allergies, goals, and budget.
- User action: Open profile page, edit fields, save.
- Files involved: `apps/users/views.py`, `apps/users/forms.py`, `apps/users/models.py`, `templates/users/profile.html`.
- URL involved: `/profile/`
- View involved: `profile_view`
- Template involved: `templates/users/profile.html`
- Model/database involved: `Profile`, `User`
- Step-by-step flow: View gets or creates profile. User submits POST. `ProfileForm` validates data. Comma-separated text is converted to JSON lists. Profile is saved. User allergy/preference fields are updated.
- Security consideration: User can edit only their own profile because the view uses `request.user`.
- How to explain it during presentation/viva: "The profile controls personalization. Allergies and likes are stored as JSON lists and used later by recipe recommendations."

## Household Member Management

- Purpose: Allow shared household planning.
- User action: Owner adds an existing user by username and role.
- Files involved: `apps/users/views.py`, `apps/users/forms.py`, `apps/users/services.py`, `apps/users/models.py`, `templates/users/household.html`.
- URL involved: `/households/`
- View involved: `household_view`
- Template involved: `templates/users/household.html`
- Model/database involved: `Household`, `HouseholdMembership`, `User`
- Step-by-step flow: View shows members. On POST, role is checked. `HouseholdInviteForm` validates username and role. `add_member_by_username()` creates or updates membership.
- Security consideration: Only owner or superuser can add members. Unique constraint prevents duplicate memberships.
- How to explain it during presentation/viva: "A household is the shared workspace, and `HouseholdMembership` controls which user belongs to it and what role they have."

## Recipe Listing And Search

- Purpose: Display available recipes and search them.
- User action: Visit recipes page or search with a query.
- Files involved: `apps/recipes/views.py`, `apps/recipes/urls.py`, `templates/recipes/index.html`.
- URL involved: `/recipes/`
- View involved: `recipes_view`
- Template involved: `templates/recipes/index.html`
- Model/database involved: `Recipe`
- Step-by-step flow: View loads public recipes and active household recipes. If `q` exists, it filters by title, description, cuisine, or diet type. Template shows recipe cards.
- Security consideration: Private recipes are filtered by household. Search uses ORM, not raw SQL.
- How to explain it during presentation/viva: "The search uses GET, so the search term appears in the URL and does not change the database."

## Recipe Create

- Purpose: Add a reusable recipe with structured ingredients.
- User action: Fill recipe form and ingredient rows.
- Files involved: `apps/recipes/views.py`, `apps/recipes/forms.py`, `apps/recipes/models.py`, `apps/nutrition/services.py`, `templates/recipes/form.html`.
- URL involved: `/recipes/new/`
- View involved: `recipe_create_view`, `_recipe_form`
- Template involved: `templates/recipes/form.html`
- Model/database involved: `Recipe`, `RecipeIngredient`, `Ingredient`
- Step-by-step flow: User submits POST. `RecipeForm` and `RecipeIngredientFormSet` validate. Recipe is saved with `created_by` and `household`. Ingredient rows are saved. Nutrition and cost are calculated.
- Security consideration: CSRF token protects the POST. Household is set server-side.
- How to explain it during presentation/viva: "A recipe is saved first, then the ingredient formset is connected to that recipe and saved."

## Recipe Detail

- Purpose: Show recipe instructions, ingredients, cost, and nutrition.
- User action: Click a recipe card.
- Files involved: `apps/recipes/views.py`, `templates/recipes/detail.html`.
- URL involved: `/recipes/<id>/`
- View involved: `recipe_detail_view`
- Template involved: `templates/recipes/detail.html`
- Model/database involved: `Recipe`, `RecipeIngredient`, `Ingredient`
- Step-by-step flow: View loads recipe if public or owned by household. Template displays instructions and related ingredients.
- Security consideration: Private recipes are protected by household filtering.
- How to explain it during presentation/viva: "The detail page uses `prefetch_related` to efficiently load recipe ingredients."

## Recipe Edit

- Purpose: Update a household recipe.
- User action: Click edit, change fields, save.
- Files involved: `apps/recipes/views.py`, `apps/recipes/forms.py`, `templates/recipes/form.html`.
- URL involved: `/recipes/<id>/edit/`
- View involved: `recipe_edit_view`, `_recipe_form`
- Template involved: `templates/recipes/form.html`
- Model/database involved: `Recipe`, `RecipeIngredient`
- Step-by-step flow: View loads the recipe by ID and household. Form and formset are filled with existing data. POST validates and updates recipe and ingredients.
- Security consideration: Only household-owned recipes can be edited.
- How to explain it during presentation/viva: "Editing uses the same form as creating, but passes `instance=recipe` so Django updates instead of creating a new row."

## Recipe Delete

- Purpose: Remove a household recipe.
- User action: Confirm delete.
- Files involved: `apps/recipes/views.py`, `templates/recipes/confirm_delete.html`.
- URL involved: `/recipes/<id>/delete/`
- View involved: `recipe_delete_view`
- Template involved: `templates/recipes/confirm_delete.html`
- Model/database involved: `Recipe`
- Step-by-step flow: View loads recipe by household. GET shows confirmation. POST calls `recipe.delete()` and redirects to recipe list.
- Security consideration: Only household-owned recipes can be deleted. CSRF token protects delete POST.
- How to explain it during presentation/viva: "Delete is protected by a confirmation page and a POST request."

## Meal Plan List

- Purpose: Show the household's meal plans.
- User action: Visit meal plans page.
- Files involved: `apps/meals/views.py`, `apps/meals/urls.py`, `templates/meals/index.html`.
- URL involved: `/meal-plans/`
- View involved: `meal_plans_view`
- Template involved: `templates/meals/index.html`
- Model/database involved: `MealPlan`
- Step-by-step flow: View gets active household. It filters meal plans by household and orders by start date. Template displays cards.
- Security consideration: `@login_required` and household filtering protect data.
- How to explain it during presentation/viva: "The list only shows plans from the logged-in user's household."

## Meal Plan Create

- Purpose: Create a new planning period.
- User action: Fill create plan form.
- Files involved: `apps/meals/views.py`, `apps/meals/forms.py`, `templates/meals/create.html`.
- URL involved: `/meal-plans/create/`
- View involved: `create_meal_plan_view`
- Template involved: `templates/meals/create.html`
- Model/database involved: `MealPlan`
- Step-by-step flow: User submits title, planning period, dates, and budget. `MealPlanForm.clean()` sets or validates end date. View saves with household and creator. User is redirected to detail page.
- Security consideration: Requires editor role. CSRF token protects POST.
- How to explain it during presentation/viva: "The planning period field is only in the form. It helps calculate the saved start and end dates."

## Meal Plan Detail

- Purpose: Display planner grid and allow adding/replacing meals.
- User action: Open a meal plan.
- Files involved: `apps/meals/views.py`, `apps/meals/forms.py`, `templates/meals/detail.html`.
- URL involved: `/meal-plans/<id>/`
- View involved: `meal_plan_detail_view`
- Template involved: `templates/meals/detail.html`
- Model/database involved: `MealPlan`, `Meal`, `MealIngredient`, `MealAnalysis`
- Step-by-step flow: View loads plan and meals, builds days and slots, calculates nutrition and budget, gets recommendations, and renders the planner.
- Security consideration: Meal plan is loaded by household. Anonymous users are blocked.
- How to explain it during presentation/viva: "The planner grid is built in the view by looping from start date to end date and creating slots for breakfast, lunch, dinner, and snack."

## Add Or Replace Meal Slot

- Purpose: Save one breakfast/lunch/dinner/snack for a date.
- User action: Submit the add meal form on plan detail.
- Files involved: `apps/meals/views.py`, `apps/meals/forms.py`, `apps/meals/services.py`, `templates/meals/detail.html`, `templates/meals/partials/ingredient_row.html`.
- URL involved: `/meal-plans/<id>/`
- View involved: `meal_plan_detail_view`
- Template involved: `templates/meals/detail.html`
- Model/database involved: `Meal`, `MealIngredient`, `MealAnalysis`, `Notification`
- Step-by-step flow: POST is validated. Existing meal in same date/type slot is deleted. New meal is saved. Custom ingredient rows are saved if needed. Meal is analyzed. Reminder is scheduled.
- Security consideration: Requires editor role. Date must be inside plan range.
- How to explain it during presentation/viva: "The unique meal slot rule means each date and meal type can only have one meal. The view replaces the old one when saving a new one."

## Custom Meal Ingredients

- Purpose: Let users plan meals that are not saved recipes.
- User action: Choose custom meal and add ingredient rows.
- Files involved: `templates/meals/partials/ingredient_row.html`, `apps/meals/services.py`, `apps/meals/models.py`.
- URL involved: `/meal-plans/<id>/`
- View involved: `meal_plan_detail_view`
- Template involved: `templates/meals/detail.html`
- Model/database involved: `MealIngredient`
- Step-by-step flow: Inputs use repeated `[]` names. `parse_rows()` reads them with `getlist()`. `sync_from_form()` creates `MealIngredient` rows.
- Security consideration: Server validates at least one custom ingredient exists.
- How to explain it during presentation/viva: "Repeated HTML input names allow many ingredient rows to be submitted in one form."

## Meal Analysis

- Purpose: Estimate nutrition, cost, benefits, risks, and confidence.
- User action: Save a meal or click refresh analysis.
- Files involved: `apps/meals/services.py`, `apps/meals/views.py`, `apps/meals/models.py`.
- URL involved: `/meal-plans/<id>/meals/<meal_id>/analyze/`
- View involved: `analyze_meal_view`
- Template involved: `templates/meals/detail.html`
- Model/database involved: `MealAnalysis`, `AIInteractionLog`
- Step-by-step flow: For saved recipe meals, analysis uses recipe nutrition. For known custom ingredients, analysis uses local ingredient nutrition. For unknown ingredients, it uses OpenAI if configured or local fallback. Analysis is saved with `update_or_create()`.
- Security consideration: Output is advisory and not medical advice. Raw prompts are not stored.
- How to explain it during presentation/viva: "The system prefers local calculations and only uses AI when information is unknown or needs estimation."

## Generate Grocery List

- Purpose: Convert meal plan ingredients into a shopping list.
- User action: Click "Generate grocery list".
- Files involved: `apps/meals/views.py`, `apps/groceries/services.py`, `apps/groceries/models.py`.
- URL involved: `/meal-plans/<id>/grocery-list/`
- View involved: `generate_grocery_list_view`
- Template involved: `templates/meals/detail.html`
- Model/database involved: `GroceryList`, `GroceryItem`, `Meal`, `RecipeIngredient`, `MealIngredient`, `PantryItem`
- Step-by-step flow: Service creates a grocery list, totals required ingredients from meals, subtracts pantry stock, creates grocery item rows, updates total cost, and redirects to grocery detail.
- Security consideration: Requires editor role and household ownership.
- How to explain it during presentation/viva: "The grocery list is generated automatically from structured data, not typed manually."

## Grocery List View

- Purpose: Show generated grocery lists and items.
- User action: Open groceries page or one grocery list.
- Files involved: `apps/groceries/views.py`, `templates/groceries/index.html`, `templates/groceries/detail.html`.
- URL involved: `/groceries/`, `/groceries/<id>/`
- View involved: `groceries_view`, `grocery_detail_view`
- Template involved: `templates/groceries/index.html`, `templates/groceries/detail.html`
- Model/database involved: `GroceryList`, `GroceryItem`
- Step-by-step flow: Views load grocery lists by household and display items with quantities and costs.
- Security consideration: Grocery list queries filter by household.
- How to explain it during presentation/viva: "The grocery detail page displays generated items and lets the user mark them purchased."

## Grocery Item Edit And Toggle

- Purpose: Adjust generated grocery item values and purchased status.
- User action: Edit item or click purchased checkbox-style button.
- Files involved: `apps/groceries/views.py`, `apps/groceries/forms.py`, `templates/groceries/item_form.html`, `templates/groceries/detail.html`.
- URL involved: `/groceries/<id>/items/<item_id>/edit/`, `/groceries/<id>/items/<item_id>/toggle/`
- View involved: `grocery_item_update_view`, `grocery_item_toggle_view`
- Template involved: `templates/groceries/item_form.html`, `templates/groceries/detail.html`
- Model/database involved: `GroceryItem`
- Step-by-step flow: Edit form updates quantity, unit, purchased, optional fields and marks manually adjusted. Toggle view flips `is_purchased`.
- Security consideration: Item must belong to a grocery list owned by active household.
- How to explain it during presentation/viva: "Generated data can still be adjusted by the user, and the app records that with `manually_adjusted`."

## Pantry CRUD

- Purpose: Track ingredients already available at home.
- User action: Add, edit, or delete pantry items.
- Files involved: `apps/pantry/views.py`, `apps/pantry/forms.py`, `apps/pantry/models.py`, `templates/pantry/index.html`, `templates/pantry/form.html`.
- URL involved: `/pantry/`, `/pantry/add/`, `/pantry/<id>/edit/`, `/pantry/<id>/delete/`
- View involved: `pantry_view`, `pantry_add_view`, `pantry_edit_view`, `pantry_delete_view`
- Template involved: `templates/pantry/index.html`, `templates/pantry/form.html`
- Model/database involved: `PantryItem`
- Step-by-step flow: List shows items. Add/edit validates `PantryItemForm`. Delete removes item on POST.
- Security consideration: Household is set server-side. Edit/delete filter by household.
- How to explain it during presentation/viva: "Pantry items reduce grocery quantities because the grocery service subtracts what is already in stock."

## Nutrition Summary

- Purpose: Show estimated nutrition totals for the latest meal plan.
- User action: Open nutrition page.
- Files involved: `apps/nutrition/views.py`, `apps/nutrition/services.py`, `templates/nutrition/index.html`.
- URL involved: `/nutrition/`
- View involved: `nutrition_view`
- Template involved: `templates/nutrition/index.html`
- Model/database involved: `MealPlan`, `Profile`, `Recipe`, `MealAnalysis`
- Step-by-step flow: View gets latest meal plan and profile. `NutritionService.meal_plan_totals()` calculates calories, protein, carbs, and fat. Template compares totals with profile goals.
- Security consideration: Uses active household.
- How to explain it during presentation/viva: "Nutrition values are estimates calculated from ingredient and recipe data."

## Budget Tracking

- Purpose: Compare generated grocery cost against budget.
- User action: Open budget page.
- Files involved: `apps/nutrition/views.py`, `apps/nutrition/services.py`, `templates/nutrition/budget.html`.
- URL involved: `/budget/` and `/nutrition/budget/`
- View involved: `budget_view`
- Template involved: `templates/nutrition/budget.html`
- Model/database involved: `MealPlan`, `GroceryList`, `Profile`
- Step-by-step flow: View loads recent meal plans. For each, it finds latest grocery list and calls `BudgetService.evaluate()`. Template shows budget, spent, and remaining.
- Security consideration: Uses active household.
- How to explain it during presentation/viva: "The budget is calculated from either the meal plan budget, the profile budget, or a default amount."

## Notifications And Reminder Preferences

- Purpose: Show reminders and allow reminder settings.
- User action: Open notifications page, mark read, or update settings.
- Files involved: `apps/notifications/views.py`, `apps/notifications/forms.py`, `apps/notifications/services.py`, `apps/notifications/tasks.py`, `templates/notifications/index.html`.
- URL involved: `/notifications/`, `/notifications/<id>/read/`
- View involved: `notifications_view`, `notification_mark_read_view`
- Template involved: `templates/notifications/index.html`
- Model/database involved: `Notification`, `NotificationPreference`
- Step-by-step flow: Notifications page loads user notifications and preferences. Preference form saves reminder times. Mark-read route updates one notification. `ReminderService.schedule()` creates reminders when meals are saved.
- Security consideration: Mark-read query includes `user=request.user`.
- How to explain it during presentation/viva: "Notifications are in-app database records, not email or SMS messages."

## AI Recipe Recommendations

- Purpose: Recommend recipes based on user profile, allergies, dislikes, and budget.
- User action: View meal plan detail or call AI API endpoint.
- Files involved: `apps/ai_services/services.py`, `apps/ai_services/urls.py`, `apps/ai_services/models.py`, `templates/meals/detail.html`.
- URL involved: `/api/v1/ai/recommendations/`
- View involved: `recommendations`
- Template involved: `templates/meals/detail.html` shows recommendations.
- Model/database involved: `Recipe`, `Profile`, `AIInteractionLog`
- Step-by-step flow: Service loads profile, filters unsafe recipes, calls OpenAI if key exists, otherwise local fallback ranks recipes. Log row is saved.
- Security consideration: Allergies and dislikes are filtered before recommendation. API is authenticated and throttled.
- How to explain it during presentation/viva: "AI is optional. The app still works without an API key because it has local fallback ranking."

## API Endpoints

- Purpose: Provide JSON access for clients outside normal HTML pages.
- User action: API client sends request with session or JWT authentication.
- Files involved: `apps/users/urls.py`, `apps/recipes/api_urls.py`, `apps/meals/api_urls.py`, `apps/groceries/api_urls.py`, `apps/notifications/api_urls.py`, `apps/ai_services/urls.py`, serializers.
- URL involved: `/api/v1/...`
- View involved: DRF function views such as `recipe_list`, `meal_plan_list`, `generate_grocery_list`, `notification_list`, `recommendations`.
- Template involved: None. APIs return JSON.
- Model/database involved: Depends on endpoint.
- Step-by-step flow: DRF authenticates request. View queries user-scoped data. Serializer converts models to dictionaries. DRF returns JSON.
- Security consideration: API endpoints use `IsAuthenticated`.
- How to explain it during presentation/viva: "The web pages render HTML, while the API endpoints return JSON for programmatic clients."

## Admin Panel

- Purpose: Let staff manage database records.
- User action: Superuser logs into `/admin/`.
- Files involved: `apps/*/admin.py`, `config/urls.py`.
- URL involved: `/admin/`
- View involved: Django built-in admin views.
- Template involved: Django admin templates.
- Model/database involved: All registered models.
- Step-by-step flow: Superuser logs in. Admin lists registered models. Staff can add, edit, search, and filter data.
- Security consideration: Only staff users can access admin.
- How to explain it during presentation/viva: "The admin panel is built into Django, but I registered my models and customized list columns and filters."

## Demo Data Seeding

- Purpose: Add sample Cameroonian ingredients and recipes.
- User action: Run a management command.
- Files involved: `apps/recipes/management/commands/seed_eatfit.py`.
- URL involved: None.
- View involved: None.
- Template involved: None.
- Model/database involved: `Ingredient`, `Recipe`, `RecipeIngredient`
- Step-by-step flow: Command creates or updates ingredients. It creates or updates recipes. It connects ingredients to recipes. It calculates nutrition totals.
- Security consideration: Run only in development/demo environments unless you intentionally want seed data.
- How to explain it during presentation/viva: "The seed command helps populate the app with demo recipes so the system is easier to test."
