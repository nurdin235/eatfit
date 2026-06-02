# 10. How To Run, Test, And Submit

This document explains how to run EatFit locally, test it, and prepare it for academic submission.

## Requirements

You need:

- Python 3.11 or compatible Python 3 version
- PostgreSQL
- Redis if testing Celery/background work
- Git optional but recommended
- A terminal or PowerShell

Python packages are listed in:

```text
requirements.txt
```

## Create A Virtual Environment

From the project root:

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Activate on Windows CMD:

```cmd
.venv\Scripts\activate
```

Activate on macOS/Linux:

```bash
source .venv/bin/activate
```

## Install Dependencies

Command:

```bash
pip install -r requirements.txt
```

If installation succeeds, Django and all project packages are available.

## Create `.env`

Copy:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

Then edit `.env` with your real local values.

Important variables:

```text
DEBUG=True
SECRET_KEY=your-local-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=eatfitsdb
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=
```

Do not submit your real `.env`.

## Set Up PostgreSQL

Create a PostgreSQL database named:

```text
eatfitsdb
```

Make sure `.env` matches your PostgreSQL setup.

Example:

```text
DB_NAME=eatfitsdb
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

## Apply Migrations

Command:

```bash
python manage.py migrate
```

What this does:

- Creates database tables
- Applies all app migrations
- Creates Django auth/session/admin tables

## Seed Demo Data

Command:

```bash
python manage.py seed_eatfit
```

What this does:

- Adds sample ingredients
- Adds sample Cameroonian recipes
- Calculates recipe nutrition and cost

## Create Superuser

Command:

```bash
python manage.py createsuperuser
```

Use this account to access:

```text
http://127.0.0.1:8000/admin/
```

## Run The Development Server

Command:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

If port 8000 is busy:

```bash
python manage.py runserver 8001
```

## Optional: Run With Docker

The project includes:

```text
docker-compose.yml
docker/Dockerfile
docker/nginx.conf
```

Command:

```bash
docker compose up --build
```

Docker services:

- PostgreSQL database
- Redis
- Django web app
- Celery worker
- Nginx

Note:

If using Docker, database host inside the web container is `db`, not `localhost`.

## Run Checks

Basic Django check:

```bash
python manage.py check
```

Migration check:

```bash
python manage.py makemigrations --check
```

Test command:

```bash
python manage.py test
```

Production deployment check:

```bash
python manage.py check --deploy
```

Note:

`check --deploy` may show warnings if local development settings are enabled. That is normal locally, but not okay for production.

## Existing Tests

Tests are in:

```text
apps/core/tests.py
```

The tests cover:

- Dashboard login requirement
- Registration creating household/profile/session
- Grocery generation
- Cross-household meal plan protection
- Reminder creation
- AI fallback logging
- Household owner membership
- Authenticated page rendering
- Custom meal ingredient saving
- Local meal analysis
- Fallback meal analysis
- Single-day meal plan end date
- View-based custom meal creation and analysis

Run them with:

```bash
python manage.py test
```

## Manual Testing Checklist

Test these in the browser:

- Register a new user.
- Log out.
- Log in again.
- Open dashboard.
- Edit profile preferences.
- Add a recipe.
- Edit a recipe.
- Delete a test recipe.
- Create a meal plan.
- Add an existing recipe meal.
- Add a custom meal with ingredients.
- Refresh meal analysis.
- Generate grocery list.
- Toggle grocery item purchased.
- Edit grocery item quantity.
- Add pantry item.
- Edit pantry item.
- Delete pantry item.
- Open nutrition page.
- Open budget page.
- Update notification preferences.
- Mark notification as read.
- Open admin panel with superuser.

## API Testing

Get JWT token:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"YOUR_USERNAME\",\"password\":\"YOUR_PASSWORD\"}"
```

Use token:

```bash
curl http://127.0.0.1:8000/api/v1/users/me/ ^
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Important API endpoints:

```text
GET /api/v1/users/me/
GET /api/v1/recipes/
GET /api/v1/meal-plans/
POST /api/v1/grocery-lists/generate/
GET /api/v1/notifications/
GET /api/v1/ai/recommendations/
```

## What To Include In Final Submission

Include:

- `apps/`
- `config/`
- `templates/`
- `static/`
- `docs/`
- `docker/`
- `manage.py`
- `requirements.txt`
- `.env.example`
- `docker-compose.yml`
- migration files
- README.md
- screenshots
- report/presentation files if required

Do not include:

- `.env`
- real passwords
- OpenAI API key
- virtual environment folder
- `__pycache__/`
- `.pyc` files
- temporary files

## Suggested Screenshots

Prepare screenshots for:

- Login page
- Register page
- Dashboard
- Profile page
- Household page
- Recipes list
- Recipe detail
- Recipe form
- Meal plans list
- Meal plan detail with planner grid
- Custom meal analysis
- Grocery list detail
- Pantry page
- Nutrition page
- Budget page
- Notifications page
- Admin panel model list

## Suggested Presentation Demo Order

1. Show login/register.
2. Show dashboard summary.
3. Show profile preferences.
4. Show recipe list and recipe detail.
5. Create a meal plan.
6. Add a custom meal.
7. Explain meal analysis.
8. Generate grocery list.
9. Show pantry effect.
10. Show nutrition and budget.
11. Show notifications.
12. Show admin panel.

## Submission Packaging

Recommended final ZIP name:

```text
EatFit_Django_Project_YourName.zip
```

Inside the ZIP:

```text
EatFit/
  apps/
  config/
  docs/
  templates/
  static/
  docker/
  manage.py
  requirements.txt
  README.md
  .env.example
  docker-compose.yml
```

## Before Zipping

Run:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Then manually confirm:

- Server starts.
- Login works.
- Registration works.
- CRUD features work.
- Admin works.
- Documentation is included.
- Screenshots are prepared.

## If The Lecturer Runs The Project

Tell them:

1. Create and activate virtual environment.
2. Install requirements.
3. Copy `.env.example` to `.env`.
4. Set PostgreSQL credentials.
5. Run migrations.
6. Seed demo data.
7. Create superuser.
8. Run server.

Commands:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py seed_eatfit
python manage.py createsuperuser
python manage.py runserver
```

## Important Beginner Note

If something fails, read the error from bottom to top. Django errors usually show:

- file name
- line number
- exact exception
- helpful message

Common fixes:

- Activate virtual environment.
- Install requirements.
- Start PostgreSQL.
- Check `.env`.
- Run migrations.
- Check URL names in templates.
