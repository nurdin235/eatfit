# EatFit

EatFit is a Django-based web application for household meal planning. It helps users manage recipes, create meal plans, add custom meals, generate grocery lists, track pantry stock, estimate nutrition, compare grocery cost with budget, and receive in-app meal reminders.

## Main Features

- User registration, login, logout, and profile management
- Household workspace with owner, editor, and viewer roles
- Recipe CRUD with structured ingredients
- Meal plan creation for single day, week, or custom range
- Add recipe-based or custom meals to meal slots
- Custom meal ingredient entry with optional prices
- Local or AI-assisted meal analysis
- Grocery list generation from meal plans
- Pantry inventory and low-stock detection
- Nutrition and budget summaries
- Notification preferences and in-app reminders
- Django admin panel
- Authenticated JSON API with JWT support

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
- django-ratelimit
- dj-database-url
- WhiteNoise
- Argon2 password hashing
- OpenAI Python SDK
- Tailwind CSS build pipeline
- HTMX pinned CDN with integrity check

## Project Structure

```text
earfit/
  apps/
    ai_services/
    core/
    groceries/
    meals/
    notifications/
    nutrition/
    pantry/
    recipes/
    users/
  config/
    settings.py
    urls.py
    celery.py
    asgi.py
    wsgi.py
  docs/
  docker/
  resources/
  services/
  static/
  templates/
  manage.py
  requirements.txt
  .env.example
  docker-compose.yml
```

## Database

The current settings use PostgreSQL:

```text
ENGINE = django.db.backends.postgresql
```

Database credentials are read from `.env`.

There is a `db.sqlite3` file in the repository, but the active configuration in `config/settings.py` uses PostgreSQL, not SQLite.

## Vercel + Supabase Deployment

This project now includes:

- `app.py` as the Vercel WSGI entrypoint
- `vercel.json` for Python runtime deployment
- `scripts/vercel_build.py` for collectstatic, deploy checks, migrations, and optional seed data
- Supabase-compatible `DATABASE_URL` support
- production static serving through WhiteNoise

Read the full deployment guide:

```text
docs/vercel_supabase_deployment.md
```

## Installation

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
npm install
npm run build:css
```

Create a `.env` file:

```bash
copy .env.example .env
```

Edit `.env` and set your PostgreSQL credentials.

## Database Setup

Create a PostgreSQL database, for example:

```text
eatfitsdb
```

Run migrations:

```bash
python manage.py migrate
```

Seed demo data:

```bash
python manage.py seed_eatfit
```

Create an admin user:

```bash
python manage.py createsuperuser
```

## Run The Server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```

## How To Use The System

1. Register a new account.
2. Log in.
3. Edit your profile preferences and budget.
4. Add or seed recipes.
5. Create a meal plan.
6. Add recipe meals or custom meals.
7. Generate a grocery list.
8. Track pantry stock.
9. Review nutrition and budget pages.
10. Check notifications and reminder settings.

## Default Test Login Details

No default login details were found in the codebase.

Create your own user with registration or create an admin user:

```bash
python manage.py createsuperuser
```

## API Endpoints

Base path:

```text
/api/v1/
```

Important endpoints:

- `POST /api/v1/auth/token/`
- `POST /api/v1/auth/token/refresh/`
- `GET /api/v1/users/me/`
- `GET /api/v1/recipes/`
- `GET /api/v1/meal-plans/`
- `POST /api/v1/grocery-lists/generate/`
- `GET /api/v1/notifications/`
- `GET /api/v1/ai/recommendations/`

API endpoints require authentication.

## Security Features

- Django password hashing
- Django sessions
- CSRF middleware and CSRF tokens in POST forms
- `@login_required` on protected pages
- Household-based query filtering
- Role checks for editing household data
- Django ORM queries instead of raw SQL
- Default template escaping against XSS
- Security headers middleware
- CSP without runtime Tailwind/Alpine inline script requirements
- Environment variables for secrets and database credentials
- Supabase SSL and serverless pooler settings
- POST-only logout
- Login/register rate limiting
- Short-lived JWT access tokens with refresh rotation
- Argon2 password hashing for new passwords
- Form and custom ingredient input limits
- JWT support for API clients
- AI logs avoid raw prompt/response storage
- AI outputs are clipped and hydrated only against server-filtered candidates

## Run Checks And Tests

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
python -m pip check
python -m pip_audit -r requirements.txt
npm audit --audit-level=moderate
```

If tests fail because PostgreSQL is not available, start PostgreSQL and verify `.env`.

## Screenshots

Add screenshots here before final submission:

- Login page
- Register page
- Dashboard
- Profile page
- Recipes page
- Meal plan detail
- Grocery list
- Pantry
- Nutrition
- Budget
- Notifications
- Admin panel

## Documentation

Beginner documentation is in `docs/`.

Recommended reading order:

1. `docs/01_PROJECT_OVERVIEW.md`
2. `docs/02_DJANGO_ARCHITECTURE_EXPLAINED.md`
3. `docs/05_URLS_VIEWS_TEMPLATES_FLOW.md`
4. `docs/06_FORMS_VALIDATION_AND_DATA_SAVING.md`
5. `docs/07_AUTHENTICATION_AUTHORIZATION_AND_SECURITY.md`
6. `docs/11_BEGINNER_VIVA_AND_PRESENTATION_GUIDE.md`

## Submission Instructions

Include:

- Source code
- `requirements.txt`
- `.env.example`
- `README.md`
- `docs/`
- migrations
- templates
- screenshots
- report/presentation files if required

Do not include:

- real `.env`
- database passwords
- API keys
- virtual environment folder
- `__pycache__`
- `.pyc` files

## Author / Student

Name:

Matric number:

Course:

Department:

Institution:

Supervisor/Lecturer:
