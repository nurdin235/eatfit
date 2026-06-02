# 02. Django Architecture Explained

This document explains Django from zero using this EatFit project as the example.

## What Django Is

Django is a Python web framework. A web framework helps you build websites faster by giving you ready-made tools for:

- URL routing
- Database models
- Forms and validation
- HTML templates
- User authentication
- Admin panel
- Security protections
- Sessions and messages

Without Django, you would have to manually write a lot of code for receiving browser requests, checking passwords, connecting to the database, creating SQL queries, rendering HTML, and protecting forms.

## What A Django Project Is

A Django project is the main configuration container for the whole website.

In this repository, the Django project is:

```text
config/
```

It contains:

- `config/settings.py`
- `config/urls.py`
- `config/wsgi.py`
- `config/asgi.py`
- `config/celery.py`

Think of the project as the control room. It decides which apps are installed, which database is used, which middleware runs, where templates are found, and which URL file receives the first request.

## What A Django App Is

A Django app is a smaller feature area inside the project.

EatFit has many apps:

- `apps.users`
- `apps.core`
- `apps.recipes`
- `apps.meals`
- `apps.groceries`
- `apps.pantry`
- `apps.nutrition`
- `apps.notifications`
- `apps.ai_services`

Each app is responsible for one part of the software. For example:

- `apps.users` handles accounts and households.
- `apps.recipes` handles recipe data.
- `apps.meals` handles meal planning.
- `apps.groceries` handles grocery lists.

## What `manage.py` Does

`manage.py` is the command-line helper for Django.

File:

```text
manage.py
```

It sets this environment variable:

```python
DJANGO_SETTINGS_MODULE = 'config.settings'
```

That tells Django to use `config/settings.py`.

Common commands:

```bash
python manage.py runserver
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py check
python manage.py seed_eatfit
```

## What `settings.py` Does

File:

```text
config/settings.py
```

This file controls project configuration.

Important settings in EatFit:

```python
INSTALLED_APPS
```

Registers Django built-in apps, third-party apps, and local EatFit apps.

```python
MIDDLEWARE
```

Lists code that runs around every request and response. EatFit uses middleware for sessions, CSRF, authentication, messages, clickjacking protection, and custom security headers.

```python
DATABASES
```

Configures PostgreSQL using environment variables.

```python
AUTH_USER_MODEL = 'users.User'
```

Tells Django to use the custom `User` model in `apps/users/models.py`.

```python
TEMPLATES
```

Tells Django to look in the root `templates/` folder.

```python
STATIC_URL`, `STATICFILES_DIRS`, `STATIC_ROOT`
```

Controls static files.

```python
REST_FRAMEWORK
```

Configures API authentication and permissions.

```python
SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`
```

Controls security behavior, especially when `DEBUG=False`.

## What `urls.py` Does

There are two kinds of URL files in this project.

Project-level URL file:

```text
config/urls.py
```

App-level URL files:

```text
apps/core/urls.py
apps/users/auth_urls.py
apps/users/urls.py
apps/meals/urls.py
apps/recipes/urls.py
apps/groceries/urls.py
apps/pantry/urls.py
apps/nutrition/urls.py
apps/notifications/urls.py
apps/*/api_urls.py
```

When a browser visits a URL, Django first checks `config/urls.py`.

Example:

```python
path('meal-plans/', include('apps.meals.urls')),
```

This means:

1. Browser visits `/meal-plans/`.
2. `config/urls.py` sees the prefix `meal-plans/`.
3. Django sends the rest of the URL to `apps/meals/urls.py`.
4. `apps/meals/urls.py` chooses the correct view.

## What `models.py` Does

A model is a Python class that represents a database table.

Example from `apps/recipes/models.py`:

```python
class Recipe(models.Model):
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    servings = models.IntegerField()
```

Django uses this model to create a database table. Each field becomes a database column.

Important EatFit models:

- `User`
- `Household`
- `HouseholdMembership`
- `Profile`
- `Ingredient`
- `Recipe`
- `RecipeIngredient`
- `MealPlan`
- `Meal`
- `MealIngredient`
- `MealAnalysis`
- `GroceryList`
- `GroceryItem`
- `PantryItem`
- `NutritionLog`
- `Budget`
- `Notification`
- `NotificationPreference`
- `AIInteractionLog`

## What `views.py` Does

A view is Python code that receives a request and returns a response.

Example from `apps/core/views.py`:

```python
@login_required
def dashboard(request):
    ...
    return render(request, 'dashboard/dashboard.html', context)
```

This means:

1. A request enters the view.
2. The view loads data from the database.
3. The view creates a context dictionary.
4. Django renders an HTML template.
5. The browser receives the final page.

## What `forms.py` Does

A form validates user input.

Example from `apps/meals/forms.py`:

```python
class MealPlanForm(forms.ModelForm):
```

This form is connected to the `MealPlan` model.

When a user submits a meal plan:

1. The browser sends POST data.
2. The view creates `MealPlanForm(request.POST)`.
3. `form.is_valid()` checks the data.
4. `form.save()` prepares or saves the model.

Forms protect the project from invalid input and help display errors in templates.

## What Templates Are

Templates are HTML files with Django template language.

Example:

```text
templates/dashboard/dashboard.html
```

Templates can display variables passed from views:

```django
{{ meal_count }}
{{ grocery_list.total_estimated_cost_xaf }}
```

Templates can also use logic:

```django
{% if active_plan %}
{% for meal in todays_meals %}
{% url 'meals:detail' active_plan.pk %}
```

## What Static Files Are

Static files are CSS, JavaScript, images, and fonts.

EatFit has a `static/` folder, but it currently has no app static files.

The layout loads external static libraries in `templates/base/base.html`:

- Tailwind CSS
- HTMX
- Alpine.js
- Google Fonts

## What Migrations Are

Migrations are Django files that describe database structure changes.

Example:

```text
apps/meals/migrations/0005_meal_entry_type_mealanalysis_mealingredient.py
```

That migration adds:

- `Meal.entry_type`
- `MealAnalysis`
- `MealIngredient`

Typical migration commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

`makemigrations` creates migration files from model changes.

`migrate` applies those migration files to the database.

## What The Database Does

The database stores the real records:

- Users
- Profiles
- Households
- Recipes
- Ingredients
- Meal plans
- Meals
- Grocery lists
- Pantry items
- Notifications
- AI logs

In current settings, EatFit uses PostgreSQL.

Although `db.sqlite3` exists, `config/settings.py` is configured for PostgreSQL.

## What The Admin Panel Does

Django admin is a built-in management interface.

URL:

```text
/admin/
```

Admin files:

```text
apps/*/admin.py
```

Examples:

- `apps/users/admin.py` registers `User`, `Household`, `Profile`, and `HouseholdMembership`.
- `apps/recipes/admin.py` registers `Recipe` and `Ingredient`.
- `apps/meals/admin.py` registers `MealPlan`, `Meal`, and `MealAnalysis`.

To use admin, create a superuser:

```bash
python manage.py createsuperuser
```

## What Request And Response Mean

A **request** is what the browser sends to Django.

Example:

```text
GET /recipes/
```

A **response** is what Django sends back.

Examples:

- HTML page
- Redirect
- JSON data
- 404 page

In views, the request is the `request` parameter:

```python
def recipes_view(request):
```

The response is returned:

```python
return render(request, 'recipes/index.html', context)
return redirect('dashboard')
```

## What GET And POST Mean

`GET` means the browser is asking to view something.

Examples:

- View dashboard
- View recipe list
- View grocery list

`POST` means the browser is submitting data that may change the database.

Examples:

- Register user
- Create meal plan
- Save recipe
- Delete pantry item
- Mark notification as read

## What CSRF Token Means

CSRF means Cross-Site Request Forgery.

Django uses CSRF tokens to make sure POST requests really came from your site form.

In templates you see:

```django
{% csrf_token %}
```

In settings you see:

```python
'django.middleware.csrf.CsrfViewMiddleware'
```

Both work together. The template sends the token. The middleware checks it.

## What ORM Means

ORM means Object Relational Mapper.

It lets you use Python instead of writing SQL manually.

Example:

```python
MealPlan.objects.filter(household=household)
```

Django converts that into SQL behind the scenes.

This helps protect against SQL injection because values are handled safely by Django.

## What Authentication Means

Authentication answers:

```text
Who are you?
```

EatFit authenticates users in:

- `apps/users/views.py`
- `CustomAuthenticationForm`
- Django session middleware
- Django password hashing

Login flow:

1. User enters username and password.
2. Django checks the password hash.
3. If valid, `login(request, user)` stores the user ID in the session.
4. Future requests know `request.user`.

## What Authorization Means

Authorization answers:

```text
What are you allowed to do?
```

EatFit authorization examples:

- `@login_required` blocks anonymous users.
- Views filter by active household.
- `assert_household_editor()` blocks users who cannot edit household data.
- `household_view()` allows only owners or superusers to add members.

## What Session Means

A session stores login state between browser requests.

After login:

```python
login(request, user)
```

Django stores a session ID in the browser cookie. On later requests, Django uses that cookie to know who the user is.

EatFit has:

```python
SESSION_COOKIE_HTTPONLY = True
```

This helps protect the session cookie from JavaScript access.

## What CRUD Means

CRUD means:

- Create
- Read
- Update
- Delete

Examples in EatFit:

- Recipes: create, read, update, delete.
- Pantry items: create, read, update, delete.
- Meal plans: create and read.
- Meals: create/replace, read, delete.
- Grocery items: read, update, toggle purchased.
- Notifications: read and mark as read.

## EatFit Request Flow

The main Django flow is:

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

Example: create meal plan.

```text
Browser submits /meal-plans/create/
-> config/urls.py includes apps.meals.urls
-> apps/meals/urls.py calls create_meal_plan_view
-> apps/meals/views.py creates MealPlanForm(request.POST)
-> form.is_valid() validates dates and planning period
-> form.save(commit=False) creates MealPlan object
-> view attaches household and created_by
-> meal_plan.save() writes to database
-> redirect to meals:detail
-> browser shows the meal plan detail page
```
