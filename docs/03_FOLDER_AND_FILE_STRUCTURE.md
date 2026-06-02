# 03. Folder And File Structure

This document explains the folders and important files in the EatFit Django project.

## Root Folder

The root folder is:

```text
earfit/
```

Important root files and folders:

```text
apps/
config/
docker/
docs/
resources/
services/
static/
templates/
.env
.env.example
db.sqlite3
docker-compose.yml
manage.py
product.docx
read_docx.py
requirements.txt
srs.docx
```

## `manage.py`

File:

```text
manage.py
```

Purpose:

- Runs Django commands.
- Points Django to `config.settings`.

Examples:

```bash
python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
```

## `requirements.txt`

File:

```text
requirements.txt
```

Purpose:

- Lists Python packages needed by the project.

Current dependencies:

```text
Django
djangorestframework
redis
celery
python-dotenv
PyJWT
django-cors-headers
djangorestframework-simplejwt
psycopg[binary]
openai
```

## `.env` And `.env.example`

Files:

```text
.env
.env.example
```

Purpose:

- `.env` stores local secrets and machine-specific settings.
- `.env.example` shows which environment variables are needed.

Important:

- Do not submit a real `.env` file with passwords or API keys.
- Submit `.env.example` instead.

Example variables:

```text
DEBUG=True
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=eatfitsdb
DB_USER=postgres
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=
```

## `db.sqlite3`

File:

```text
db.sqlite3
```

Purpose:

- SQLite database file.

Important:

The current `config/settings.py` uses PostgreSQL, not SQLite. So `db.sqlite3` is not the active database under the current settings.

## `config/`

Folder:

```text
config/
```

This is the Django project folder.

### `config/settings.py`

Purpose:

- Installed apps
- Middleware
- Database
- Templates
- Static files
- Authentication settings
- REST Framework settings
- Celery settings
- Security settings

### `config/urls.py`

Purpose:

- Main URL router for the whole project.
- Sends each URL prefix to the correct app.

Examples:

```python
path('', include('apps.core.urls'))
path('auth/', include('apps.users.auth_urls'))
path('meal-plans/', include('apps.meals.urls'))
path('api/v1/recipes/', include('apps.recipes.api_urls'))
```

### `config/wsgi.py`

Purpose:

- Entry point for traditional WSGI servers such as Gunicorn.

### `config/asgi.py`

Purpose:

- Entry point for ASGI servers.

### `config/celery.py`

Purpose:

- Configures Celery background task processing.
- Uses settings with the `CELERY_` namespace.

## `apps/`

Folder:

```text
apps/
```

This contains all local Django apps.

## `apps/core/`

Purpose:

- Dashboard
- Custom security headers middleware
- Core tests

Files:

```text
apps/core/views.py
apps/core/urls.py
apps/core/middleware.py
apps/core/tests.py
apps/core/apps.py
```

Important behavior:

- `dashboard()` collects active meal plan, today's meals, nutrition totals, grocery cost, low stock count, unread notifications, and meal count.
- `SecurityHeadersMiddleware` adds headers like CSP, Referrer-Policy, and Permissions-Policy.

## `apps/users/`

Purpose:

- User accounts
- Authentication
- Profiles
- Households
- Household roles
- User API

Files:

```text
apps/users/models.py
apps/users/forms.py
apps/users/views.py
apps/users/auth_urls.py
apps/users/urls.py
apps/users/services.py
apps/users/signals.py
apps/users/serializers.py
apps/users/admin.py
apps/users/apps.py
apps/users/migrations/
```

Important models:

- `User`
- `Household`
- `HouseholdMembership`
- `Profile`

Important views:

- `register_view`
- `login_view`
- `logout_view`
- `profile_view`
- `household_view`

## `apps/recipes/`

Purpose:

- Ingredients
- Recipes
- Recipe ingredients
- Recipe CRUD
- Recipe API
- Demo data seed command

Files:

```text
apps/recipes/models.py
apps/recipes/forms.py
apps/recipes/views.py
apps/recipes/urls.py
apps/recipes/api_urls.py
apps/recipes/serializers.py
apps/recipes/admin.py
apps/recipes/management/commands/seed_eatfit.py
apps/recipes/migrations/
```

Important models:

- `Ingredient`
- `Recipe`
- `RecipeIngredient`

Important templates:

- `templates/recipes/index.html`
- `templates/recipes/detail.html`
- `templates/recipes/form.html`
- `templates/recipes/confirm_delete.html`

## `apps/meals/`

Purpose:

- Meal plans
- Meals
- Custom meal ingredients
- Meal analysis
- Grocery generation trigger
- Meal plan API

Files:

```text
apps/meals/models.py
apps/meals/forms.py
apps/meals/views.py
apps/meals/services.py
apps/meals/urls.py
apps/meals/api_urls.py
apps/meals/serializers.py
apps/meals/admin.py
apps/meals/migrations/
```

Important models:

- `MealPlan`
- `Meal`
- `MealIngredient`
- `MealAnalysis`

Important templates:

- `templates/meals/index.html`
- `templates/meals/create.html`
- `templates/meals/detail.html`
- `templates/meals/partials/ingredient_row.html`

## `apps/groceries/`

Purpose:

- Grocery lists
- Grocery items
- Grocery generation service
- Grocery API

Files:

```text
apps/groceries/models.py
apps/groceries/forms.py
apps/groceries/views.py
apps/groceries/services.py
apps/groceries/urls.py
apps/groceries/api_urls.py
apps/groceries/serializers.py
apps/groceries/admin.py
apps/groceries/migrations/
```

Important models:

- `GroceryList`
- `GroceryItem`

Important templates:

- `templates/groceries/index.html`
- `templates/groceries/detail.html`
- `templates/groceries/item_form.html`

## `apps/pantry/`

Purpose:

- Household pantry stock
- Pantry CRUD

Files:

```text
apps/pantry/models.py
apps/pantry/forms.py
apps/pantry/views.py
apps/pantry/urls.py
apps/pantry/admin.py
apps/pantry/migrations/
```

Important model:

- `PantryItem`

Important templates:

- `templates/pantry/index.html`
- `templates/pantry/form.html`

## `apps/nutrition/`

Purpose:

- Nutrition totals
- Budget calculations
- Budget page

Files:

```text
apps/nutrition/models.py
apps/nutrition/views.py
apps/nutrition/services.py
apps/nutrition/urls.py
apps/nutrition/admin.py
apps/nutrition/migrations/
```

Important models:

- `NutritionLog`
- `Budget`

Important templates:

- `templates/nutrition/index.html`
- `templates/nutrition/budget.html`

## `apps/notifications/`

Purpose:

- Notifications
- Notification preferences
- Reminder scheduling
- Celery task
- Notification API

Files:

```text
apps/notifications/models.py
apps/notifications/forms.py
apps/notifications/views.py
apps/notifications/services.py
apps/notifications/tasks.py
apps/notifications/urls.py
apps/notifications/api_urls.py
apps/notifications/admin.py
apps/notifications/migrations/
```

Important models:

- `Notification`
- `NotificationPreference`

Important template:

- `templates/notifications/index.html`

## `apps/ai_services/`

Purpose:

- AI recommendation service
- AI interaction log model
- AI API endpoint

Files:

```text
apps/ai_services/models.py
apps/ai_services/services.py
apps/ai_services/urls.py
apps/ai_services/admin.py
apps/ai_services/migrations/
```

Important model:

- `AIInteractionLog`

Important endpoint:

```text
GET /api/v1/ai/recommendations/
```

## `services/`

Folder:

```text
services/
```

Contains:

```text
services/ai_service.py
```

This is a compatibility wrapper:

```python
class AIService(OpenAIRecommendationService):
    pass
```

It allows older imports to use `AIService` while the real implementation lives in `apps/ai_services/services.py`.

## `templates/`

Folder:

```text
templates/
```

This folder contains HTML pages.

Main template groups:

```text
templates/base/
templates/partials/
templates/auth/
templates/dashboard/
templates/users/
templates/recipes/
templates/meals/
templates/groceries/
templates/pantry/
templates/nutrition/
templates/notifications/
```

### Base Template

File:

```text
templates/base/base.html
```

Purpose:

- Main page layout
- Loads Tailwind, HTMX, Alpine.js, and Google Fonts
- Includes navbar, sidebar, alerts, and footer
- Provides `{% block content %}` where each page inserts its own content

### Partials

Folder:

```text
templates/partials/
```

Purpose:

- Reusable pieces like navbar, sidebar, footer, alerts, loading spinner, and AI badge.

## `static/`

Folder:

```text
static/
```

Purpose:

- Static files such as CSS, JavaScript, and images.

Current finding:

- No static files were found inside `static/`.
- The app uses CDN-based Tailwind, HTMX, Alpine.js, and Google Fonts.

## `docs/`

Folder:

```text
docs/
```

Purpose:

- Documentation for architecture, security, APIs, diagrams, beginner explanations, rebuild guide, viva preparation, and submission checklist.

Existing docs were kept, and the new numbered beginner guides were added.

## `docker/` And `docker-compose.yml`

Files:

```text
docker/Dockerfile
docker/nginx.conf
docker-compose.yml
```

Purpose:

- Run the app with Docker.
- Services include PostgreSQL, Redis, Django web app, Celery worker, and Nginx.

Important Docker services:

- `db`
- `redis`
- `web`
- `celery`
- `nginx`

## `resources/`

Folder:

```text
resources/
```

Purpose:

- Reference design files, downloaded resources, documents, and images.

Important:

- These files are not currently used as Django app templates or static assets.

## Word Documents

Files:

```text
srs.docx
product.docx
resources/Stitch - Projects_files/srs.docx
```

Purpose:

- Likely academic or project planning documents.

## `read_docx.py`

File:

```text
read_docx.py
```

Purpose:

- Helper script for reading text from a `.docx` file.
- It is not part of the running Django app.

## File Types Found

The project contains:

- Python files
- HTML templates
- Markdown documentation
- Docker files
- `.env` files
- Word documents
- Images and downloaded resource files
- SQLite database file

## Important Beginner Rule

When trying to understand the project, read files in this order:

1. `README.md`
2. `docs/01_PROJECT_OVERVIEW.md`
3. `config/settings.py`
4. `config/urls.py`
5. `apps/users/models.py`
6. `apps/recipes/models.py`
7. `apps/meals/models.py`
8. `apps/*/views.py`
9. `apps/*/forms.py`
10. `templates/base/base.html`
11. Feature templates such as `templates/meals/detail.html`
