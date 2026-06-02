# EatFit Architecture

EatFit is now a Django monolith with clear app boundaries and server-rendered pages enhanced by HTMX.

## Runtime Components
- Browser: Django templates, Tailwind, Alpine, HTMX.
- Django app: page views, DRF JSON endpoints, session auth, CSRF, domain services.
- PostgreSQL: local database managed through pgAdmin and accessed only by Django.
- Redis: planned broker/cache backend for scheduled work.
- OpenAI: backend-only advisory recommendation provider.

## Domain Services
- `GroceryGenerationService.generate(meal_plan)` aggregates recipe ingredients, subtracts pantry stock, and estimates cost.
- `MealIngredientService.sync_from_form(meal, rows)` stores one-off custom meal ingredients from dynamic planner rows.
- `MealAnalysisService.analyze(meal)` creates local or OpenAI-estimated nutrition, benefits, risks, and advisory summaries.
- `MealCostService.calculate(meal)` calculates recipe-based or custom ingredient costs.
- `NutritionService.calculate_recipe(recipe)` and `meal_plan_totals(meal_plan)` calculate informational macros.
- `BudgetService.evaluate(meal_plan)` compares grocery totals against profile or plan budgets.
- `ReminderService.schedule(meal)` creates in-app reminder notifications for household members.
- `OpenAIRecommendationService.rank_recipes(user)` filters unsafe candidates, calls OpenAI when configured, and otherwise uses local ranking.

## Data Model
- `Household` and `HouseholdMembership` enforce shared access and owner/editor/viewer roles.
- `Profile` stores diet type, allergies, likes/dislikes, nutrition targets, timezone, and budget.
- `Recipe`, `Ingredient`, and `RecipeIngredient` keep ingredients structured for grocery and nutrition calculations.
- `MealPlan` and `Meal` represent weekly planning slots.
- `MealIngredient` stores custom one-off meal ingredients entered directly by users.
- `MealAnalysis` stores advisory nutrition strength, benefits, risks, estimated macros, and cost per meal.
- `GroceryList` and `GroceryItem` store generated lists and user edits.
- `NotificationPreference` and `Notification` power in-app reminders.
- `AIInteractionLog` stores only safe metadata: operation, provider, model, status, input hash, summary, and metadata.

## Local Setup
1. Create a PostgreSQL database in pgAdmin, for example `eatfitsdb`.
2. Copy `.env.example` to `.env` and fill `DB_PASSWORD`.
3. Run `python manage.py migrate`.
4. Run `python manage.py seed_eatfit`.
5. Start with `python manage.py runserver`.
