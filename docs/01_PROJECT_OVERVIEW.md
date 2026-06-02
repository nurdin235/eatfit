# 01. Project Overview

## Project Name

The software is called **EatFit**.

The repository folder is named `earfit`, but the application title shown in templates and documentation is **EatFit - Web-Based Meal Planning Application**.

The Django project module is:

```text
config/
```

This means `config/settings.py`, `config/urls.py`, `config/wsgi.py`, and `config/asgi.py` are the main project-level files.

## What EatFit Does

EatFit is a Django web application for household meal planning. A user can register, log in, manage their profile, create meal plans, add recipes or custom meals, generate grocery lists, track pantry stock, check nutrition and budget estimates, and receive in-app meal reminders.

The project also has API endpoints using Django REST Framework and JWT tokens.

## Main Features

- User registration, login, logout, and profile management.
- Household management with owner, editor, and viewer roles.
- Recipe management with ingredients, cost estimates, and nutrition estimates.
- Meal plan creation for one day, one week, or a custom date range.
- Meal slot management for breakfast, lunch, dinner, and snacks.
- Custom meal entry with free-text ingredients and optional prices.
- Automatic meal analysis using local calculations or OpenAI fallback.
- Grocery list generation from meal plan ingredients.
- Pantry inventory tracking and low-stock warnings.
- Nutrition and budget summary pages.
- Notification preferences and meal reminder notifications.
- API endpoints for users, recipes, meal plans, grocery generation, notifications, and AI recommendations.
- Django admin configuration for managing database records.
- Docker configuration for PostgreSQL, Redis, web, Celery, and Nginx.

## Technologies Used

- Python
- Django 5.2 LTS
- Django REST Framework
- djangorestframework-simplejwt
- PostgreSQL
- Redis
- Celery
- python-dotenv
- django-cors-headers
- OpenAI Python SDK
- Tailwind CSS through CDN
- HTMX through CDN
- Alpine.js through CDN

Dependencies are listed in `requirements.txt`.

## Important Project Folders

```text
config/
```

Main Django project configuration.

```text
apps/
```

All local Django apps live here.

```text
templates/
```

HTML templates used by Django views.

```text
static/
```

Static asset folder. In this project it currently exists but contains no app static files.

```text
docs/
```

Project documentation. This folder now contains beginner guides for understanding, rebuilding, presenting, and submitting the project.

```text
docker/
```

Dockerfile and Nginx configuration.

```text
resources/
```

Reference materials and design/source resources. These are not loaded directly by Django routes.

## Django Apps In This Project

### `apps.core`

Purpose: dashboard and shared core behavior.

Important files:

- `apps/core/views.py`
- `apps/core/urls.py`
- `apps/core/middleware.py`
- `apps/core/tests.py`

Main feature:

- Dashboard at `/`

### `apps.users`

Purpose: custom user model, authentication, profile, household, roles, and user API.

Important files:

- `apps/users/models.py`
- `apps/users/forms.py`
- `apps/users/views.py`
- `apps/users/auth_urls.py`
- `apps/users/urls.py`
- `apps/users/services.py`
- `apps/users/signals.py`
- `apps/users/admin.py`

Main features:

- Register
- Login
- Logout
- Profile editing
- Household member management
- API endpoint for current user

### `apps.recipes`

Purpose: recipe, ingredient, and recipe ingredient management.

Important files:

- `apps/recipes/models.py`
- `apps/recipes/forms.py`
- `apps/recipes/views.py`
- `apps/recipes/urls.py`
- `apps/recipes/api_urls.py`
- `apps/recipes/management/commands/seed_eatfit.py`

Main features:

- List recipes
- Search recipes
- Create recipe
- View recipe details
- Edit recipe
- Delete recipe
- Seed demo Cameroonian recipes and ingredients

### `apps.meals`

Purpose: meal planning, meal slots, custom ingredients, meal analysis, and meal plan API.

Important files:

- `apps/meals/models.py`
- `apps/meals/forms.py`
- `apps/meals/views.py`
- `apps/meals/services.py`
- `apps/meals/urls.py`
- `apps/meals/api_urls.py`

Main features:

- Create meal plans
- Add or replace meal slots
- Delete meals
- Analyze meals
- Create custom meals with custom ingredients
- Generate grocery lists from meal plans

### `apps.groceries`

Purpose: grocery list and grocery item management.

Important files:

- `apps/groceries/models.py`
- `apps/groceries/forms.py`
- `apps/groceries/views.py`
- `apps/groceries/services.py`
- `apps/groceries/urls.py`
- `apps/groceries/api_urls.py`

Main features:

- View grocery lists
- View grocery list details
- Edit grocery items
- Toggle purchased status
- Generate grocery lists through web and API

### `apps.pantry`

Purpose: household pantry inventory.

Important files:

- `apps/pantry/models.py`
- `apps/pantry/forms.py`
- `apps/pantry/views.py`
- `apps/pantry/urls.py`

Main features:

- List pantry stock
- Add pantry item
- Edit pantry item
- Delete pantry item
- Detect low stock

### `apps.nutrition`

Purpose: nutrition and budget calculations.

Important files:

- `apps/nutrition/models.py`
- `apps/nutrition/views.py`
- `apps/nutrition/services.py`
- `apps/nutrition/urls.py`

Main features:

- Nutrition summary
- Budget tracking
- Recipe nutrition calculation
- Meal plan nutrition totals

### `apps.notifications`

Purpose: in-app notifications and reminder preferences.

Important files:

- `apps/notifications/models.py`
- `apps/notifications/forms.py`
- `apps/notifications/views.py`
- `apps/notifications/services.py`
- `apps/notifications/tasks.py`
- `apps/notifications/urls.py`
- `apps/notifications/api_urls.py`

Main features:

- Notification inbox
- Mark notification as read
- Meal reminder preferences
- Celery task to mark due notifications as sent

### `apps.ai_services`

Purpose: OpenAI-backed recipe ranking and AI usage logs.

Important files:

- `apps/ai_services/models.py`
- `apps/ai_services/services.py`
- `apps/ai_services/urls.py`
- `apps/ai_services/admin.py`

Main features:

- Allergy-aware recipe recommendations
- OpenAI recommendation service
- Local fallback recommendation ranking
- AI interaction audit logs

## How The User Experiences The App

1. User opens the site.
2. If not logged in, Django redirects them to `/auth/login/`.
3. User registers or logs in.
4. Django stores login state in the session.
5. User lands on the dashboard.
6. User creates recipes, meal plans, pantry items, and grocery lists.
7. Django saves data in the PostgreSQL database using the ORM.
8. Templates display updated records back to the browser.

## Important Note About The Database

There is a `db.sqlite3` file in the repository, but `config/settings.py` is currently configured to use **PostgreSQL**, not SQLite.

Current database configuration:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        ...
    }
}
```

So for the current settings, the active database is PostgreSQL. The `db.sqlite3` file may be an older local database file and should not be treated as the main active database unless the settings are changed.

## API Support

The project includes API routes under:

```text
/api/v1/
```

Important API routes:

- `POST /api/v1/auth/token/`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/users/me/`
- `GET /api/v1/meal-plans/`
- `GET /api/v1/recipes/`
- `POST /api/v1/grocery-lists/generate/`
- `GET /api/v1/notifications/`
- `GET /api/v1/ai/recommendations/`

## File Upload Functionality

I did not find active file upload fields such as `FileField`, `ImageField`, `request.FILES`, or upload views in the Django apps.

So this project currently does **not** implement user file upload functionality.

## Static Files

The `static/` folder exists, but no static files were found inside it during analysis.

The UI currently relies mainly on external CDN scripts and styles loaded in `templates/base/base.html`:

- Tailwind CSS
- HTMX
- Alpine.js
- Google Fonts

## Final Submission Summary

For final submission, you should include:

- Source code
- `requirements.txt`
- `README.md`
- `docs/`
- Migrations
- `.env.example`
- Screenshots
- Report or presentation files if required by your lecturer

Do not submit:

- Real `.env` secrets
- Virtual environment folder
- Database passwords
- API keys
- `__pycache__`
- Large unnecessary generated files
