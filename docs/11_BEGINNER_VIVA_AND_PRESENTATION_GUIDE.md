# 11. Beginner Viva And Presentation Guide

This guide helps you explain EatFit confidently during a viva or project presentation.

The goal is to sound like a student who understands the project, not like someone reading copied theory.

## Simple Project Explanation

EatFit is a web-based meal planning application built with Django.

It helps a household plan meals, manage recipes, generate grocery lists, track pantry stock, estimate nutrition, compare grocery cost with budget, and receive meal reminders.

Users can register, log in, create a household workspace, add recipes, create meal plans, add custom meals, and generate grocery lists automatically from planned meals.

## Simple Architecture Explanation

You can say:

"EatFit follows Django's MTV pattern. The models define the database tables, the views handle requests and business flow, and the templates display HTML pages. When a user submits a form, the URL router sends the request to a view, the view validates a form, saves or reads models using the ORM, and returns a rendered template or redirect."

## MTV Architecture

Django uses MTV:

- Model
- Template
- View

### Model

Models define database tables.

Example:

```text
apps/meals/models.py
```

`MealPlan` stores a planning period. `Meal` stores one breakfast, lunch, dinner, or snack.

### Template

Templates display HTML.

Example:

```text
templates/meals/detail.html
```

This page displays the meal planner grid and the add-meal form.

### View

Views receive requests and return responses.

Example:

```text
apps/meals/views.py
```

`meal_plan_detail_view()` loads a meal plan, validates submitted meals, saves meals, analyzes them, and renders the detail page.

## How To Explain The Request Flow

Say:

"The browser sends a request to a URL. Django checks `config/urls.py`, then sends the request to the app's `urls.py`. The URL maps to a view function. The view may use a form to validate POST data, then it reads or writes model objects. Finally, it returns either a template response or a redirect."

Example:

```text
Browser
-> /meal-plans/create/
-> config/urls.py
-> apps/meals/urls.py
-> create_meal_plan_view
-> MealPlanForm
-> MealPlan model
-> database
-> redirect to meal detail
```

## How To Explain Database Saving

Use this exact example:

"When the user creates a meal plan, the form in `templates/meals/create.html` sends a POST request to `/meal-plans/create/`. In `apps/meals/views.py`, `create_meal_plan_view` receives `request.POST` and puts it into `MealPlanForm`. If `form.is_valid()` returns true, the view uses `form.save(commit=False)` to create a `MealPlan` object without saving immediately. Then the view adds the household and created_by user, because those should be controlled by the server. Finally, `meal_plan.save()` writes the record to PostgreSQL through Django's ORM."

Important sentence:

"The ORM converts Python model operations into SQL queries."

## How To Explain Authentication

Say:

"Authentication means checking who the user is. EatFit uses Django's built-in authentication system with a custom user model. Registration uses `CustomUserCreationForm`, which hashes passwords safely. Login uses Django's authentication form and `login(request, user)` to store the user in the session."

Files:

- `apps/users/models.py`
- `apps/users/forms.py`
- `apps/users/views.py`
- `templates/auth/login.html`
- `templates/auth/register.html`

## How To Explain Authorization

Say:

"Authorization means checking what the logged-in user is allowed to access. EatFit uses `@login_required` to block anonymous users. It also filters records by active household, for example `get_object_or_404(MealPlan, pk=pk, household=household)`. For editing, it checks roles with `assert_household_editor()`."

Important examples:

- Only owners can add household members.
- Editors can create meal plans and generate grocery lists.
- Users cannot view another household's meal plan by changing the URL ID.

## How To Explain Security Features

Say:

"The project uses Django security features such as password hashing, CSRF tokens, sessions, template escaping, and ORM queries. Most pages are protected by `@login_required`. POST forms include `{% csrf_token %}`. Household data is filtered by the active household. API endpoints require authentication. There is also custom middleware that adds security headers."

Security files:

- `config/settings.py`
- `apps/core/middleware.py`
- `apps/users/services.py`

Security weakness to be honest about:

"Logout uses a POST form protected by CSRF, so another website cannot sign a user out with a simple link or image request."

That answer sounds honest and mature.

## How To Explain CRUD

CRUD means:

- Create
- Read
- Update
- Delete

EatFit examples:

- Recipes have full CRUD.
- Pantry items have full CRUD.
- Meal plans can be created and viewed.
- Meals can be added/replaced and deleted.
- Grocery items can be updated and toggled purchased.

Say:

"For example, pantry CRUD is handled in `apps/pantry/views.py`. `pantry_add_view` creates, `pantry_view` reads, `pantry_edit_view` updates, and `pantry_delete_view` deletes pantry items."

## How To Explain Templates

Say:

"Templates are HTML files that Django fills with data from views. EatFit has a base template at `templates/base/base.html`. Other templates extend it, so the navbar, sidebar, alerts, and footer are shared. The page-specific content goes inside `{% block content %}`."

Example:

```django
{% extends "base/base.html" %}
{% block content %}
...
{% endblock %}
```

## How To Explain Migrations

Say:

"Migrations are files that record changes to the database structure. When I create or change a model, I run `python manage.py makemigrations`. Then I run `python manage.py migrate` to apply those changes to the database."

Example:

```text
apps/meals/migrations/0005_meal_entry_type_mealanalysis_mealingredient.py
```

This migration added custom meal support and meal analysis tables.

## How To Explain Admin Panel

Say:

"Django admin is a built-in dashboard for staff users. In EatFit, each app has an `admin.py` file where models are registered. For example, `apps/recipes/admin.py` registers recipes and ingredients, and `apps/meals/admin.py` registers meal plans, meals, and meal analysis. I can create a superuser with `python manage.py createsuperuser` and manage data at `/admin/`."

## How To Explain Grocery Generation

Say:

"The grocery list is generated from meal plan data. In `GroceryGenerationService.generate()`, the system reads all meals in a plan. For recipe meals, it reads `RecipeIngredient` rows. For custom meals, it reads `MealIngredient` rows. Then it subtracts matching pantry stock and creates `GroceryItem` rows. Finally, it saves the total estimated cost on the `GroceryList`."

Files:

- `apps/groceries/services.py`
- `apps/meals/views.py`
- `apps/groceries/models.py`

## How To Explain Meal Analysis

Say:

"Meal analysis is handled by `MealAnalysisService` in `apps/meals/services.py`. If the meal uses a saved recipe, the system calculates nutrition from saved recipe values. If it is a custom meal with known ingredients, it calculates from ingredient nutrition data. If there are unknown ingredients, it can use OpenAI if an API key is configured, otherwise it uses a local fallback estimate. The result is saved in `MealAnalysis`."

Important:

"The analysis is advisory and not medical advice."

## How To Explain AI Recommendations

Say:

"AI recommendations are optional. The service first filters recipes against allergies and dislikes. If an OpenAI API key exists, it asks OpenAI to rank recipes. If no key exists, it uses a local fallback ranking. The project logs only safe metadata in `AIInteractionLog`, not raw prompts or responses."

Files:

- `apps/ai_services/services.py`
- `apps/ai_services/models.py`
- `apps/ai_services/urls.py`

## Common Lecturer Questions And Strong Answers

### Question: What is the difference between a Django project and a Django app?

Answer:

"The project is the main configuration container. In EatFit, the project is `config`. Apps are feature modules inside the project, like `users`, `recipes`, `meals`, and `groceries`."

### Question: Why did you use multiple apps?

Answer:

"I used multiple apps to separate responsibilities. User logic is in `users`, meal planning is in `meals`, grocery logic is in `groceries`, and recipe logic is in `recipes`. This makes the project easier to understand and maintain."

### Question: How is a meal plan saved?

Answer:

"The user submits `MealPlanForm`. The view validates it, uses `form.save(commit=False)`, adds household and created_by, then calls `save()`. Django ORM writes the row to PostgreSQL."

### Question: How do you prevent users from seeing other households' data?

Answer:

"Views filter records by active household. For example, meal plan detail uses `get_object_or_404(MealPlan, pk=pk, household=household)`. If the plan does not belong to the user's household, Django returns 404."

### Question: What does CSRF token do?

Answer:

"It protects POST forms from cross-site request forgery. The template sends `{% csrf_token %}` and Django's CSRF middleware verifies it."

### Question: What is the ORM?

Answer:

"The ORM lets me use Python classes and methods to work with the database instead of writing SQL directly. For example, `Recipe.objects.filter(is_public=True)` becomes a SQL query behind the scenes."

### Question: What are migrations?

Answer:

"Migrations are versioned database structure changes. They let another person rebuild the same database tables by running `python manage.py migrate`."

### Question: Where is business logic placed?

Answer:

"Simple request logic is in views, but larger business logic is placed in services. For example, grocery generation is in `apps/groceries/services.py`, and meal analysis is in `apps/meals/services.py`."

### Question: Is there an API?

Answer:

"Yes. API routes are under `/api/v1/`. They use Django REST Framework and require authentication through session auth or JWT."

### Question: Does the project upload files?

Answer:

"No. I did not find active `FileField`, `ImageField`, or `request.FILES` usage. The current project does not implement file upload."

### Question: What database does it use?

Answer:

"The settings are configured for PostgreSQL using environment variables. There is a `db.sqlite3` file in the repository, but current settings use PostgreSQL."

## Two-Minute Presentation Script

"Good day. My project is EatFit, a web-based meal planning application built with Django. The purpose is to help a household plan meals, manage recipes, generate grocery lists, track pantry stock, and monitor nutrition and budget.

The project uses Django's MTV architecture. Models define database tables such as User, Household, Recipe, MealPlan, Meal, GroceryList, PantryItem, and Notification. Views handle requests, validate forms, call services, and return templates. Templates display the interface using a shared base layout.

Users can register and log in. After registration, the system automatically creates a household and profile. A user can create recipes with structured ingredients, create a meal plan, add recipe meals or custom meals, and generate a grocery list. Grocery generation reads the planned meals, subtracts pantry stock, and saves grocery items.

For security, the project uses Django password hashing, sessions, CSRF tokens, login-required views, household filtering, and role checks. The project also has API endpoints under `/api/v1/` and an optional AI recommendation service with local fallback.

Overall, EatFit is a Django monolith organized into feature apps, with clear separation between models, forms, views, templates, services, and APIs."

## Five-Minute Presentation Script

"Good day. My project is EatFit, a web-based meal planning application developed with Django. It is designed for a household that wants to plan meals, manage recipes, generate grocery lists, track pantry stock, and understand estimated nutrition and budget impact.

The system starts with authentication. A user can register through `CustomUserCreationForm`. Django hashes the password, creates the user, and then the application creates a household and profile for that user. Login uses Django's authentication system and sessions, so after login the user is available as `request.user`.

The project is organized into multiple Django apps. The `users` app handles accounts, profiles, households, and roles. The `recipes` app handles ingredients and reusable recipes. The `meals` app handles meal plans, meal slots, custom ingredients, and meal analysis. The `groceries` app handles generated grocery lists. The `pantry` app tracks stock already available at home. The `nutrition` app calculates totals and budgets. The `notifications` app handles reminders. The `ai_services` app handles optional AI recommendations.

The main data flow follows Django MTV. For example, when creating a meal plan, the browser submits a POST request to `/meal-plans/create/`. The URL router calls `create_meal_plan_view`. The view creates a `MealPlanForm`, validates it, uses `form.save(commit=False)`, attaches the active household and user, then saves the model. Django ORM converts that save into SQL and stores it in PostgreSQL.

One strong feature is grocery generation. The service reads all meals in a plan. If a meal is based on a saved recipe, it reads recipe ingredients. If it is a custom meal, it reads custom meal ingredients. It subtracts pantry stock and creates grocery items with estimated costs.

Security is handled through Django features and custom checks. Most pages use `@login_required`. Data is filtered by active household, so users cannot access another household's records. Editing uses role checks such as `assert_household_editor`. Forms include CSRF tokens. Templates use default escaping, and database access uses the ORM.

The project also includes API endpoints using Django REST Framework and JWT authentication. Finally, there is documentation, tests, migrations, admin configuration, and Docker support for a more complete submission."

## Technical Explanation Script

"Technically, EatFit is a Django 5 project with the project module named `config`. `config/settings.py` registers Django built-in apps, DRF, CORS headers, and local apps. The active database engine is PostgreSQL, configured through environment variables loaded by `python-dotenv`.

The custom user model is `apps.users.models.User`, configured by `AUTH_USER_MODEL = 'users.User'`. The user belongs to a `Household`, and `HouseholdMembership` stores roles. Most feature models are household-scoped.

Routing begins in `config/urls.py`, which includes app-specific URL files. Page views return templates, while API views return JSON responses through DRF. Templates extend `templates/base/base.html`, which includes the shared navbar, sidebar, alerts, and footer.

For data saving, views generally use Django ModelForms. The important pattern is `form.save(commit=False)`, used when the server must attach fields such as `household` or `created_by`. This prevents the browser from controlling ownership fields.

Business logic is separated into service classes. `GroceryGenerationService` handles grocery list creation. `MealAnalysisService` handles nutrition analysis. `NutritionService` calculates totals. `BudgetService` compares planned cost to budget. `ReminderService` creates notifications. `OpenAIRecommendationService` handles optional AI ranking with local fallback.

Security is layered: authentication through Django sessions, authorization through `@login_required`, household query filtering, role checks, CSRF middleware, ORM-based queries, template escaping, security headers, and API authentication. Known improvement areas are logout as POST-only and stricter production settings."

## Final Viva Confidence Tips

- Do not memorize every line.
- Focus on flow: URL -> view -> form -> model -> template.
- Use actual file names when answering.
- Be honest about improvements.
- If asked a question you do not know, connect it to what you do know.

Example:

"I do not remember the exact line number, but that logic is in `apps/meals/views.py`, inside `meal_plan_detail_view`, where the meal form is validated and saved."

That sounds much better than guessing.
