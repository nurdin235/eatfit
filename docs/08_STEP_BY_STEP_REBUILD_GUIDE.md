# 08. Step By Step Rebuild Guide

This guide explains how to rebuild EatFit from zero.

It is written for a beginner. The exact code will take time to recreate, but this guide explains the correct order and why each step matters.

## Step 1. Create The Project Folder

Command:

```bash
mkdir eatfit
cd eatfit
```

Why:

You need one root folder to hold the Django project.

What happens internally:

Nothing Django-related yet. You are only creating a workspace.

Common error:

If the folder already exists, choose another folder name or enter the existing one.

## Step 2. Create A Virtual Environment

Command on Windows:

```bash
python -m venv .venv
```

Why:

A virtual environment keeps this project's Python packages separate from other projects.

What happens internally:

Python creates a local environment folder with its own Python executable and package directory.

Common error:

If `python` is not recognized, install Python or try:

```bash
py -m venv .venv
```

## Step 3. Activate The Virtual Environment

Command on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Command on Windows CMD:

```cmd
.venv\Scripts\activate
```

Command on macOS/Linux:

```bash
source .venv/bin/activate
```

Why:

After activation, packages install inside `.venv`.

Common error:

PowerShell may block scripts. You can use:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try activation again.

## Step 4. Install Django And Dependencies

Command:

```bash
pip install Django==5.2.14 djangorestframework==3.17.1 redis==5.0.3 celery==5.6.3 python-dotenv==1.2.2 PyJWT==2.13.0 django-cors-headers==4.9.0 django-ratelimit==4.1.0 djangorestframework-simplejwt==5.5.1 psycopg[binary]==3.3.4 dj-database-url==3.1.2 whitenoise==6.12.0 argon2-cffi==25.1.0 openai==2.40.0
```

Then save dependencies:

```bash
pip freeze > requirements.txt
```

Why:

These packages are used by the current project.

What happens internally:

Pip downloads and installs Python libraries into the virtual environment.

Common error:

If PostgreSQL driver installation fails, make sure you install:

```bash
psycopg[binary]
```

not just `psycopg`.

## Step 5. Start The Django Project

Command:

```bash
django-admin startproject config .
```

Why:

This creates the main Django project files.

Files created:

```text
manage.py
config/settings.py
config/urls.py
config/asgi.py
config/wsgi.py
```

What happens internally:

Django creates the project configuration module named `config`.

## Step 6. Create The Apps Folder

Command:

```bash
mkdir apps
```

Why:

EatFit stores all local apps inside `apps/`.

Create marker file:

```bash
type nul > apps\__init__.py
```

On macOS/Linux:

```bash
touch apps/__init__.py
```

Why:

This makes `apps` importable as a Python package.

## Step 7. Start Django Apps

Commands:

```bash
python manage.py startapp users apps/users
python manage.py startapp core apps/core
python manage.py startapp recipes apps/recipes
python manage.py startapp meals apps/meals
python manage.py startapp groceries apps/groceries
python manage.py startapp pantry apps/pantry
python manage.py startapp nutrition apps/nutrition
python manage.py startapp notifications apps/notifications
python manage.py startapp ai_services apps/ai_services
```

Why:

Each app owns one feature area.

Common error:

Django may require the destination folder to exist first. If so, create each folder before running `startapp`.

## Step 8. Update Each `apps.py`

Example:

```python
class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
```

Why:

Because apps are inside the `apps/` package, their full Python path is `apps.users`, not just `users`.

## Step 9. Register Apps In `settings.py`

File:

```text
config/settings.py
```

Add:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'corsheaders',
    'apps.users.apps.UsersConfig',
    'apps.meals.apps.MealsConfig',
    'apps.recipes.apps.RecipesConfig',
    'apps.groceries.apps.GroceriesConfig',
    'apps.pantry.apps.PantryConfig',
    'apps.nutrition.apps.NutritionConfig',
    'apps.ai_services.apps.AiServicesConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.core.apps.CoreConfig',
]
```

Why:

Django only uses apps listed in `INSTALLED_APPS`.

Common error:

If you forget to register an app, its models will not get migrations.

## Step 10. Configure Environment Variables

Install dotenv:

```bash
pip install python-dotenv
```

In `config/settings.py`, load `.env`:

```python
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env')
```

Create `.env.example`:

```text
DEBUG=True
SECRET_KEY=replace-with-a-long-random-secret
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=eatfitsdb
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=
```

Why:

Secrets and database passwords should not be hard-coded.

## Step 11. Configure The Database

In `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'eatfitsdb'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Why:

EatFit is designed to run on PostgreSQL.

What happens internally:

Django uses this configuration whenever it needs to read or write database records.

Common error:

If PostgreSQL is not running, migrations and tests may fail with connection errors.

Fix:

- Start PostgreSQL.
- Check `.env`.
- Check database exists.
- Check username and password.

## Step 12. Create The Custom User Model

File:

```text
apps/users/models.py
```

Create:

- `Household`
- `User(AbstractUser)`
- `HouseholdMembership`
- `Profile`

In `settings.py`, add:

```python
AUTH_USER_MODEL = 'users.User'
```

Why:

EatFit needs extra user fields like household, dietary preferences, and allergies.

Important beginner warning:

Create the custom user model before the first migration. Changing user model later is difficult.

## Step 13. Create Recipe Models

File:

```text
apps/recipes/models.py
```

Create:

- `Ingredient`
- `Recipe`
- `RecipeIngredient`

Why:

Recipes need structured ingredients so the app can calculate cost, nutrition, and grocery lists.

## Step 14. Create Meal Models

File:

```text
apps/meals/models.py
```

Create:

- `MealPlan`
- `Meal`
- `MealIngredient`
- `MealAnalysis`

Why:

These models store the meal planning calendar and custom meal analysis.

## Step 15. Create Grocery, Pantry, Nutrition, Notification, And AI Models

Files:

```text
apps/groceries/models.py
apps/pantry/models.py
apps/nutrition/models.py
apps/notifications/models.py
apps/ai_services/models.py
```

Create:

- `GroceryList`
- `GroceryItem`
- `PantryItem`
- `NutritionLog`
- `Budget`
- `Notification`
- `NotificationPreference`
- `AIInteractionLog`

Why:

These complete the feature data model.

## Step 16. Make Migrations

Command:

```bash
python manage.py makemigrations
```

Why:

Django reads your models and creates migration files.

What happens internally:

Django compares model code with previous migrations and writes operations like `CreateModel`, `AddField`, and `AddConstraint`.

Common error:

Circular migration dependencies can happen when many apps reference each other.

Fix:

Create models in a careful order and let Django split initial migrations if needed.

## Step 17. Apply Migrations

Command:

```bash
python manage.py migrate
```

Why:

This creates the actual database tables.

What happens internally:

Django runs SQL against PostgreSQL based on migration files.

Common error:

Database connection refused.

Fix:

Start PostgreSQL or Docker database service.

## Step 18. Create Forms

Files:

```text
apps/users/forms.py
apps/recipes/forms.py
apps/meals/forms.py
apps/groceries/forms.py
apps/pantry/forms.py
apps/notifications/forms.py
```

Create forms:

- `CustomUserCreationForm`
- `CustomAuthenticationForm`
- `ProfileForm`
- `HouseholdInviteForm`
- `RecipeForm`
- `RecipeIngredientFormSet`
- `MealPlanForm`
- `MealForm`
- `GroceryItemForm`
- `PantryItemForm`
- `NotificationPreferenceForm`

Why:

Forms validate user input before saving data.

## Step 19. Create Views

Files:

```text
apps/core/views.py
apps/users/views.py
apps/recipes/views.py
apps/meals/views.py
apps/groceries/views.py
apps/pantry/views.py
apps/nutrition/views.py
apps/notifications/views.py
```

Why:

Views receive requests, call forms/services/models, and return templates or redirects.

Common pattern:

```python
if request.method == 'POST':
    form = SomeForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        return redirect(...)
else:
    form = SomeForm()
return render(request, 'template.html', {'form': form})
```

## Step 20. Create URLs

Files:

```text
config/urls.py
apps/core/urls.py
apps/users/auth_urls.py
apps/users/urls.py
apps/recipes/urls.py
apps/meals/urls.py
apps/groceries/urls.py
apps/pantry/urls.py
apps/nutrition/urls.py
apps/notifications/urls.py
apps/*/api_urls.py
```

Why:

URLs connect browser paths to view functions.

Example:

```python
path('create/', views.create_meal_plan_view, name='create')
```

Common error:

`NoReverseMatch`

Meaning:

A template used a URL name that does not exist or missed a namespace.

Fix:

Check `app_name` and the `{% url %}` tag.

## Step 21. Create Templates

Folder:

```text
templates/
```

Create:

- `templates/base/base.html`
- `templates/partials/navbar.html`
- `templates/partials/sidebar.html`
- `templates/partials/alerts.html`
- `templates/partials/footer.html`
- `templates/auth/login.html`
- `templates/auth/register.html`
- feature templates for each app

Why:

Templates display HTML pages to users.

Important:

In `settings.py`, configure:

```python
'DIRS': [BASE_DIR / 'templates']
```

## Step 22. Add Static Files

Folder:

```text
static/
```

In this current project, the folder exists but is empty. Styling is loaded through CDNs in `base.html`.

If you add local CSS later:

```text
static/css/style.css
```

Then in template:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

## Step 23. Add Authentication

In `apps/users/views.py`, create:

- `register_view`
- `login_view`
- `logout_view`

In templates, add:

- `templates/auth/register.html`
- `templates/auth/login.html`

In `settings.py`, add:

```python
LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'auth:login'
```

Why:

Users must log in before accessing private household data.

## Step 24. Add Authorization

Use:

```python
@login_required
```

Use household filtering:

```python
get_object_or_404(MealPlan, pk=pk, household=household)
```

Use role checks:

```python
assert_household_editor(request.user, household)
```

Why:

Authentication only proves identity. Authorization controls access.

## Step 25. Add Services

Service files:

```text
apps/users/services.py
apps/groceries/services.py
apps/meals/services.py
apps/nutrition/services.py
apps/notifications/services.py
apps/ai_services/services.py
```

Why:

Services hold business logic that is too large for views.

Examples:

- Grocery generation
- Meal analysis
- Nutrition totals
- Budget evaluation
- Reminder scheduling
- AI recommendations

## Step 26. Add API Endpoints

Use Django REST Framework.

Files:

```text
apps/users/urls.py
apps/recipes/api_urls.py
apps/meals/api_urls.py
apps/groceries/api_urls.py
apps/notifications/api_urls.py
apps/ai_services/urls.py
```

In `settings.py`, configure:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (...),
    'DEFAULT_PERMISSION_CLASSES': (...),
}
```

Why:

APIs allow non-template clients to read or create data.

## Step 27. Configure Admin

Files:

```text
apps/*/admin.py
```

Register models:

```python
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ...
```

Why:

Admin lets staff manage database records quickly.

## Step 28. Create Superuser

Command:

```bash
python manage.py createsuperuser
```

Why:

You need a staff/admin account to access `/admin/`.

Common error:

If custom user migrations are not applied, superuser creation fails.

Fix:

Run:

```bash
python manage.py migrate
```

## Step 29. Seed Demo Data

File:

```text
apps/recipes/management/commands/seed_eatfit.py
```

Command:

```bash
python manage.py seed_eatfit
```

Why:

It creates demo Cameroonian ingredients and recipes.

What happens internally:

- `Ingredient.objects.update_or_create()`
- `Recipe.objects.update_or_create()`
- `RecipeIngredient.objects.update_or_create()`
- `NutritionService.calculate_recipe()`

## Step 30. Run The Server

Command:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

What happens internally:

Django starts a development server and listens for browser requests.

Common error:

Port already in use.

Fix:

```bash
python manage.py runserver 8001
```

## Step 31. Test The System

Commands:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

Manual tests:

- Register
- Login
- Create profile
- Create recipe
- Create meal plan
- Add custom meal
- Generate grocery list
- Add pantry item
- Check nutrition
- Check budget
- Check notifications
- Login to admin

## Step 32. Prepare Final Submission

Include:

- Source code
- `requirements.txt`
- `.env.example`
- migrations
- templates
- docs
- README
- screenshots
- report/presentation

Do not include:

- `.env`
- virtual environment
- passwords
- API keys
- cache files
- `__pycache__`

## Common Errors And Fixes

### Error: `ModuleNotFoundError`

Cause:

Package not installed or virtual environment not active.

Fix:

```bash
pip install -r requirements.txt
```

### Error: `relation does not exist`

Cause:

Database tables have not been created.

Fix:

```bash
python manage.py migrate
```

### Error: `no such table`

Cause:

Same as above, usually SQLite or missing migrations.

Fix:

```bash
python manage.py migrate
```

### Error: `NoReverseMatch`

Cause:

Wrong URL name in template.

Fix:

Check `app_name`, `urlpatterns`, and `{% url %}`.

### Error: `CSRF verification failed`

Cause:

Missing CSRF token in POST form.

Fix:

Add:

```django
{% csrf_token %}
```

### Error: PostgreSQL connection refused

Cause:

PostgreSQL is not running or `.env` settings are wrong.

Fix:

- Start PostgreSQL.
- Confirm database name.
- Confirm username/password.
- Confirm host and port.

### Error: Static files not loading in production

Cause:

Static files not collected.

Fix:

```bash
python manage.py collectstatic
```

## Best Learning Order

To rebuild confidently, learn in this order:

1. Models
2. Migrations
3. Admin
4. Forms
5. Views
6. URLs
7. Templates
8. Authentication
9. Authorization
10. Services
11. APIs
12. Tests
