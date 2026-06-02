# 04. Database And Models Explained

This document explains how EatFit stores data.

## What A Database Is

A database is where the application permanently stores information.

Examples of EatFit data:

- User accounts
- Password hashes
- Households
- Profiles
- Recipes
- Ingredients
- Meal plans
- Meals
- Grocery lists
- Pantry items
- Notifications
- AI logs

## Current Database Configuration

File:

```text
config/settings.py
```

EatFit is configured to use PostgreSQL:

```python
'ENGINE': 'django.db.backends.postgresql'
```

Database values come from environment variables:

```python
DB_NAME
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
```

There is a `db.sqlite3` file in the project, but it is not the active database with the current settings.

## What A Model Is

A Django model is a Python class that maps to a database table.

Example:

```python
class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
```

Django turns this into a database table with a `name` column.

## What The ORM Is

ORM means Object Relational Mapper.

It lets you write Python like this:

```python
Recipe.objects.filter(is_public=True)
```

instead of writing SQL manually.

Django converts the Python query into SQL and sends it to the database.

## App: Users

File:

```text
apps/users/models.py
```

### `Household`

Purpose:

Stores a shared family or household workspace.

Fields:

- `name`: household name.
- `invite_code`: unique code generated automatically.
- `created_at`: when the household was created.
- `updated_at`: when the household was last updated.

Important method:

```python
save()
```

If `invite_code` is empty, it generates one using `token_urlsafe(12)`.

How it is used:

- Every user needs a household.
- Meal plans, recipes, pantry items, grocery lists, and budgets are attached to households.

### `User`

Purpose:

Custom user model for EatFit.

It extends:

```python
AbstractUser
```

That means it already has fields like:

- `username`
- `password`
- `email`
- `first_name`
- `last_name`
- `is_staff`
- `is_superuser`

Extra EatFit fields:

- `household`: optional direct link to one household.
- `dietary_preferences`: JSON dictionary.
- `allergies`: JSON list.

Important property:

```python
active_household
```

It returns the direct household if present. If not, it looks at `HouseholdMembership`.

Important method:

```python
ensure_household()
```

It makes sure the user has a household. If they do not, it creates:

- a new `Household`
- a `HouseholdMembership`
- a direct `user.household` link

### `HouseholdMembership`

Purpose:

Connects users to households and stores their role.

Fields:

- `user`
- `household`
- `role`
- `joined_at`

Roles:

- `owner`
- `editor`
- `viewer`

Constraint:

```python
UniqueConstraint(fields=['user', 'household'])
```

This prevents the same user from being added to the same household twice.

### `Profile`

Purpose:

Stores nutrition and preference data for a user.

Fields:

- `user`: one-to-one link with `User`.
- `diet_type`: none, vegetarian, vegan, keto, high protein, or low carb.
- `allergies`: JSON list.
- `likes`: JSON list.
- `dislikes`: JSON list.
- `calorie_goal`
- `protein_goal`
- `carbs_goal`
- `fat_goal`
- `weekly_budget_xaf`
- `timezone`
- `measurement_system`
- `updated_at`

Important method:

```python
preference_summary()
```

Returns a small dictionary used by recommendation and filtering services.

## App: Recipes

File:

```text
apps/recipes/models.py
```

### `Ingredient`

Purpose:

Stores reusable food ingredients.

Fields:

- `name`: unique ingredient name.
- `category`: example values: vegetable, protein, grain.
- `default_unit`: example: g, ml, pcs.
- `estimated_cost_per_unit_xaf`
- `calories_per_unit`
- `protein_per_unit`
- `carbs_per_unit`
- `fat_per_unit`
- `created_at`

Used by:

- Recipes
- Pantry items
- Grocery items
- Custom meal ingredients
- Nutrition calculations

### `Recipe`

Purpose:

Stores reusable meals.

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
- `allergens`: JSON list.
- `tags`: JSON list.
- `estimated_cost_xaf`
- `calories`
- `protein`
- `carbs`
- `fat`
- `created_by`
- `household`
- `is_public`
- `is_cameroonian`
- `created_at`
- `updated_at`

Important property:

```python
total_time
```

Returns:

```python
prep_time + cook_time
```

Used in templates like `templates/recipes/index.html`.

### `RecipeIngredient`

Purpose:

Join table between `Recipe` and `Ingredient`.

Fields:

- `recipe`
- `ingredient`
- `quantity`
- `unit`

Constraint:

```python
UniqueConstraint(fields=['recipe', 'ingredient', 'unit'])
```

This means the same ingredient and unit should not be duplicated inside one recipe.

## App: Meals

File:

```text
apps/meals/models.py
```

### `MealPlan`

Purpose:

Stores a dated plan for a household.

Fields:

- `household`
- `title`
- `start_date`
- `end_date`
- `created_by`
- `is_ai_generated`
- `status`
- `weekly_budget_xaf`
- `created_at`
- `updated_at`

Status choices:

- `draft`
- `active`
- `archived`

Ordering:

```python
ordering = ['-start_date']
```

Newest plans appear first.

### `Meal`

Purpose:

Stores one planned meal slot inside a meal plan.

Fields:

- `meal_plan`
- `entry_type`: recipe or custom.
- `recipe`: optional link to `Recipe`.
- `recipe_name`: saved title for recipe or custom meal.
- `date`
- `meal_type`: breakfast, lunch, dinner, or snack.
- `servings`
- `source`: manual or AI.
- `is_ai_suggested`
- `ai_reason`
- `notes`
- `created_at`

Constraint:

```python
UniqueConstraint(fields=['meal_plan', 'date', 'meal_type'])
```

This prevents two breakfasts on the same date in the same meal plan.

### `MealIngredient`

Purpose:

Stores ingredients for a custom meal.

Fields:

- `meal`
- `ingredient`: optional link to known `Ingredient`.
- `name`: free-text ingredient name.
- `quantity`
- `unit`
- `unit_price_xaf`
- `total_price_xaf`
- `created_at`

Important method:

```python
save()
```

Before saving, it calculates:

```python
total_price_xaf = unit_price_xaf * quantity
```

If `ingredient` exists and `name` is blank, it copies the ingredient name.

### `MealAnalysis`

Purpose:

Stores nutrition, cost, benefit, and risk analysis for one meal.

Relationship:

```python
meal = OneToOneField(Meal)
```

One meal has one latest analysis row.

Fields:

- `calories`
- `protein`
- `carbs`
- `fat`
- `estimated_total_cost_xaf`
- `nutrition_strength_score`
- `nutrition_strength`
- `health_benefits`: JSON list.
- `health_risks`: JSON list.
- `advisory_summary`
- `limitations`: JSON list.
- `confidence`
- `is_estimated`
- `provider`
- `status`
- `metadata`
- `created_at`
- `updated_at`

Status choices:

- `local`
- `ai`
- `fallback`
- `error`

## App: Groceries

File:

```text
apps/groceries/models.py
```

### `GroceryList`

Purpose:

Stores a shopping list generated from a meal plan.

Fields:

- `household`
- `meal_plan`
- `created_at`
- `updated_at`
- `status`
- `total_estimated_cost_xaf`
- `generated_by`
- `is_ai_optimized`

Status choices:

- `open`
- `shopping`
- `completed`

### `GroceryItem`

Purpose:

Stores one item in a grocery list.

Fields:

- `grocery_list`
- `ingredient`
- `quantity`
- `unit`
- `estimated_cost_xaf`
- `manually_adjusted`
- `is_purchased`
- `is_optional`

Constraint:

```python
UniqueConstraint(fields=['grocery_list', 'ingredient', 'unit'])
```

This prevents duplicate lines for the same ingredient and unit in one grocery list.

## App: Pantry

File:

```text
apps/pantry/models.py
```

### `PantryItem`

Purpose:

Stores ingredients already available in the household.

Fields:

- `household`
- `ingredient`
- `quantity`
- `unit`
- `expiry_date`
- `low_stock_threshold`

Property:

```python
is_low_stock
```

Returns `True` when:

```python
quantity <= low_stock_threshold
```

Constraint:

```python
UniqueConstraint(fields=['household', 'ingredient', 'unit'])
```

This prevents duplicate pantry rows for the same ingredient and unit in one household.

## App: Nutrition

File:

```text
apps/nutrition/models.py
```

### `NutritionLog`

Purpose:

Stores daily nutrition numbers for a user.

Fields:

- `user`
- `meal`
- `date`
- `calories`
- `protein`
- `carbs`
- `fat`

This model exists, but most current nutrition totals are calculated from recipes and meals by `NutritionService`.

### `Budget`

Purpose:

Stores a budget amount for a user and household over a period.

Fields:

- `user`
- `household`
- `period_start`
- `period_end`
- `amount_xaf`
- `created_at`

Current budget pages mainly use `BudgetService.evaluate()` with meal plan and profile budget values.

## App: Notifications

File:

```text
apps/notifications/models.py
```

### `Notification`

Purpose:

Stores in-app notifications for users.

Fields:

- `user`
- `notification_type`
- `title`
- `message`
- `action_url`
- `scheduled_for`
- `sent_at`
- `is_read`
- `created_at`

Notification types:

- `meal_reminder`
- `grocery`
- `budget`
- `system`

### `NotificationPreference`

Purpose:

Stores reminder settings for one user.

Fields:

- `user`
- `meal_reminders_enabled`
- `breakfast_time`
- `lunch_time`
- `dinner_time`
- `reminder_minutes_before`
- `updated_at`

Used by:

```text
apps/notifications/services.py
```

## App: AI Services

File:

```text
apps/ai_services/models.py
```

### `AIInteractionLog`

Purpose:

Stores safe audit records for AI operations.

Fields:

- `user`
- `operation`
- `provider`
- `model`
- `status`
- `input_hash`
- `output_summary`
- `metadata`
- `created_at`

Important:

The current model stores summaries and hashes, not raw prompts or raw AI responses.

Status choices:

- `success`
- `fallback`
- `error`

## Main Relationships

### User And Household

```text
User -> Household
User -> HouseholdMembership -> Household
User -> Profile
```

A user has a profile and belongs to a household.

### Recipes

```text
Recipe -> RecipeIngredient -> Ingredient
```

A recipe has many ingredients through `RecipeIngredient`.

### Meal Planning

```text
Household -> MealPlan -> Meal
Meal -> Recipe
Meal -> MealIngredient
Meal -> MealAnalysis
```

A household owns meal plans. A meal plan contains meals. A meal can be based on a saved recipe or custom ingredients.

### Grocery Generation

```text
MealPlan -> GroceryList -> GroceryItem -> Ingredient
Household -> PantryItem -> Ingredient
```

Grocery generation reads meals and pantry items, then creates grocery items.

### Notifications

```text
User -> Notification
User -> NotificationPreference
```

Users receive notifications and configure reminder times.

## How Data Is Saved

Example: creating a meal plan.

1. User fills `templates/meals/create.html`.
2. Browser sends POST data to `/meal-plans/create/`.
3. `apps/meals/urls.py` maps the URL to `create_meal_plan_view`.
4. The view creates `MealPlanForm(request.POST)`.
5. `form.is_valid()` checks dates and planning period.
6. `form.save(commit=False)` creates a `MealPlan` object but does not save yet.
7. The view sets:

```python
meal_plan.household = household
meal_plan.created_by = request.user
```

8. `meal_plan.save()` writes the row to the database.
9. Django ORM converts the save into SQL.
10. User is redirected to the meal plan detail page.

## Important Constraints

Constraints protect data quality.

Examples:

- A user can have one membership per household.
- A meal plan can have only one meal per date and meal type.
- A recipe cannot have duplicate ingredient and unit rows.
- A grocery list cannot have duplicate ingredient and unit rows.
- A household pantry cannot duplicate the same ingredient and unit.

## Migrations

Each app has a `migrations/` folder.

Migration files tell Django how to create and update database tables.

Examples:

- `apps/users/migrations/0001_initial.py`
- `apps/users/migrations/0002_household_invite_code_household_updated_at_and_more.py`
- `apps/meals/migrations/0005_meal_entry_type_mealanalysis_mealingredient.py`
- `apps/recipes/migrations/0002_ingredient_calories_per_unit_and_more.py`

Do not delete migrations before submission. They are needed to rebuild the database.
