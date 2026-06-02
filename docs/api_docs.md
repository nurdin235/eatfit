# EatFit API Documentation

Base path: `/api/v1/`

Authentication:
- Template pages use Django session authentication and CSRF.
- JSON endpoints use DRF authentication with session auth and JWT bearer tokens.
- JWT endpoints:
  - `POST /api/v1/auth/token/`
  - `POST /api/v1/auth/token/refresh/`

## Users
- `GET /api/v1/users/me/` returns the authenticated user profile summary.

## Recipes
- `GET /api/v1/recipes/` lists public recipes plus recipes owned by the active household.

## Meal Plans
- `GET /api/v1/meal-plans/` lists meal plans for the active household only.

Page routes:
- `GET /meal-plans/ingredient-row/` returns an HTMX ingredient row partial for custom meal entry.
- `POST /meal-plans/{plan_id}/meals/{meal_id}/analyze/` refreshes advisory analysis for a meal.

Custom meals:
- Users may add a meal with `entry_type=custom`, `recipe_name`, date, meal type, servings, and repeated `ingredient_name[]`, `ingredient_quantity[]`, `ingredient_unit[]`, and optional `ingredient_unit_price_xaf[]` fields.
- Analysis runs after save and is advisory only.

## Grocery Lists
- `POST /api/v1/grocery-lists/generate/`
  - Body: `{"meal_plan_id": 1}`
  - Generates a grocery list by aggregating structured recipe ingredients and subtracting matching pantry stock.

## Notifications
- `GET /api/v1/notifications/` lists the authenticated user’s in-app notifications.

## AI
- `GET /api/v1/ai/recommendations/`
  - Returns allergy-filtered recipe recommendations.
  - Uses OpenAI when `OPENAI_API_KEY` is configured.
  - Falls back to deterministic local ranking when no API key is present.
  - Raw prompts and raw model outputs are not stored.
