# 07. Authentication, Authorization, And Security

This document explains the security parts of EatFit in beginner-friendly language.

## Authentication

Authentication means:

```text
Who are you?
```

In EatFit, users prove who they are by logging in with a username and password.

Important files:

- `apps/users/views.py`
- `apps/users/forms.py`
- `apps/users/models.py`
- `templates/auth/login.html`
- `templates/auth/register.html`
- `config/settings.py`

Important functions:

- `register_view`
- `login_view`
- `logout_view`

## Password Hashing

EatFit uses Django's authentication system.

When a user registers, the password is not stored as plain text.

The form:

```python
CustomUserCreationForm(UserCreationForm)
```

uses Django's safe password system.

Django stores a password hash in the database. A password hash is a one-way encoded version of the password.

This means even the database does not store the original password.

## Login Sessions

When a user logs in, this code runs:

```python
login(request, user)
```

Django stores the login in a session.

The browser receives a session cookie. On later requests, Django uses that cookie to know the logged-in user.

Important setting:

```python
SESSION_COOKIE_HTTPONLY = True
```

This helps prevent JavaScript from reading the session cookie.

## Authorization

Authorization means:

```text
What are you allowed to do?
```

In EatFit, authorization is handled with:

- `@login_required`
- household filtering
- role checks
- `get_object_or_404()`
- custom service functions

## `@login_required`

This decorator blocks anonymous users.

Example:

```python
@login_required
def dashboard(request):
```

If the user is not logged in, Django redirects to:

```python
LOGIN_URL = 'auth:login'
```

Pages protected by `@login_required` include:

- Dashboard
- Profile
- Household
- Meal plans
- Recipes
- Groceries
- Pantry
- Nutrition
- Budget
- Notifications

## Household Data Protection

EatFit is a household-based app. Most records belong to a household.

Important service:

```text
apps/users/services.py
```

Function:

```python
get_active_household(user)
```

Views use the active household to filter records.

Example from meal plan detail:

```python
meal_plan = get_object_or_404(MealPlan, pk=pk, household=household)
```

This means a user cannot view another household's meal plan by guessing its ID.

## Role-Based Authorization

File:

```text
apps/users/models.py
```

Model:

```python
HouseholdMembership
```

Roles:

- `owner`
- `editor`
- `viewer`

File:

```text
apps/users/services.py
```

Important functions:

```python
assert_household_editor(user, household)
assert_household_member(user, household)
user_role(user, household)
```

Examples:

- Creating a meal plan requires editor role.
- Adding meals requires editor role.
- Generating grocery lists requires editor role.
- Adding household members requires owner role or superuser.

## CSRF Protection

CSRF means Cross-Site Request Forgery.

Django protects POST forms with CSRF tokens.

Middleware in `config/settings.py`:

```python
'django.middleware.csrf.CsrfViewMiddleware'
```

Templates include:

```django
{% csrf_token %}
```

Examples:

- `templates/auth/register.html`
- `templates/auth/login.html`
- `templates/meals/create.html`
- `templates/meals/detail.html`
- `templates/recipes/form.html`
- `templates/pantry/form.html`
- `templates/groceries/item_form.html`
- `templates/notifications/index.html`

## Input Validation

Input validation happens in forms.

Examples:

### Registration Email Validation

File:

```text
apps/users/forms.py
```

Method:

```python
clean_email()
```

It rejects duplicate email addresses.

### Meal Plan Date Validation

File:

```text
apps/meals/forms.py
```

Method:

```python
MealPlanForm.clean()
```

It checks:

- single-day plans end on the start date
- weekly plans end six days after start date
- custom range has an end date
- end date is not before start date

### Meal Form Validation

File:

```text
apps/meals/forms.py
```

Method:

```python
MealForm.clean()
```

It checks:

- recipe meals must select a recipe
- custom meals must have a title

Additional validation in `meal_plan_detail_view` checks:

- date is inside the plan range
- custom meals have at least one ingredient

## SQL Injection Protection

EatFit uses Django ORM queries.

Examples:

```python
Recipe.objects.filter(Q(is_public=True) | Q(household=household))
MealPlan.objects.filter(household=household)
get_object_or_404(GroceryList, pk=pk, household=household)
```

Django safely parameterizes database values. This helps protect against SQL injection.

I did not find raw SQL queries in the app code.

## XSS Protection

XSS means Cross-Site Scripting.

Django templates escape variables by default.

Example:

```django
{{ recipe.title }}
```

If a user enters HTML in a title, Django normally displays it as text instead of executing it.

I did not find obvious dangerous use of the `safe` filter in the templates.

## Security Headers

File:

```text
apps/core/middleware.py
```

Middleware:

```python
SecurityHeadersMiddleware
```

It adds:

- `Referrer-Policy`
- `Permissions-Policy`
- `Content-Security-Policy`

These headers help reduce browser-based attacks.

## Clickjacking Protection

Middleware:

```python
'django.middleware.clickjacking.XFrameOptionsMiddleware'
```

Setting:

```python
X_FRAME_OPTIONS = 'DENY'
```

This helps prevent other websites from embedding EatFit inside hidden frames.

## HTTPS And Secure Cookies

File:

```text
config/settings.py
```

Important settings:

```python
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False if DEBUG else True)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_CONTENT_TYPE_NOSNIFF = True
```

Meaning:

- In local development with `DEBUG=True`, strict HTTPS settings are relaxed.
- In production with `DEBUG=False`, secure cookies and SSL redirect become stricter by default.

## API Security

File:

```text
config/settings.py
```

REST Framework settings:

```python
DEFAULT_AUTHENTICATION_CLASSES = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
)
DEFAULT_PERMISSION_CLASSES = (
    'rest_framework.permissions.IsAuthenticated',
)
```

Meaning:

- API clients must be authenticated.
- Browser sessions and JWT tokens are accepted.

JWT routes:

```text
POST /api/v1/auth/token/
POST /api/v1/auth/token/refresh/
```

## AI Security

Files:

- `apps/ai_services/services.py`
- `apps/ai_services/models.py`
- `apps/meals/services.py`

Good practices found:

- OpenAI API key is read from environment variables.
- Raw prompts and raw responses are not stored in `AIInteractionLog`.
- AI logs store operation, provider, model, status, input hash, output summary, and metadata.
- Allergy and dislike filtering happens before recipe recommendations.
- If no OpenAI key is configured, local fallback ranking is used.
- Meal analysis labels estimates as advisory and not medical advice.
- API recommendations have a throttle class.

## File Upload Security

I did not find active file upload functionality.

No active use of:

- `FileField`
- `ImageField`
- `request.FILES`

Because uploads are not implemented, there are no current upload validation rules.

If uploads are added later, validate:

- file type
- file size
- storage location
- user ownership
- virus/malware risk

## Admin Panel Security

Admin route:

```text
/admin/
```

Admin access is controlled by Django:

- user must be authenticated
- user must be staff
- superuser has full permissions

Admin files:

- `apps/users/admin.py`
- `apps/recipes/admin.py`
- `apps/meals/admin.py`
- `apps/groceries/admin.py`
- `apps/pantry/admin.py`
- `apps/nutrition/admin.py`
- `apps/notifications/admin.py`
- `apps/ai_services/admin.py`

Create admin user:

```bash
python manage.py createsuperuser
```

## Security Issues Or Weaknesses Found

### 1. `DEBUG` Defaults To `True`

Current setting:

```python
DEBUG = env_bool('DEBUG', True)
```

Why it matters:

If `DEBUG=True` in production, Django may show detailed error pages.

Suggested fix:

For production `.env`:

```text
DEBUG=False
```

For stronger code safety, you could make production fail if `DEBUG` is missing.

Change applied:

- No behavior change applied. This is documented because changing defaults can break local beginner setup.

### 2. `SECRET_KEY` Has A Random Fallback

Current setting:

```python
SECRET_KEY = os.environ.get('SECRET_KEY') or get_random_secret_key()
```

Why it matters:

If `.env` is missing, Django still starts with a random secret. This is convenient locally, but sessions can break after restart because the key changes.

Suggested fix:

For production, always set:

```text
SECRET_KEY=your-long-random-secret
```

Optional stronger code pattern:

```python
if not DEBUG and not os.environ.get('SECRET_KEY'):
    raise RuntimeError('SECRET_KEY is required when DEBUG=False')
```

Change applied:

- Added an explanatory code comment only.

### 3. Logout Uses A GET Link

Current template:

```text
templates/partials/navbar.html
```

The logout action is linked with:

```django
<a href="{% url 'auth:logout' %}">
```

Why it matters:

Best practice is to make logout a POST action protected by CSRF, because it changes session state.

Suggested fix:

Use a small POST form:

```django
<form method="post" action="{% url 'auth:logout' %}">
    {% csrf_token %}
    <button type="submit">Sign out</button>
</form>
```

And make `logout_view` accept POST only.

Change applied:

- No behavior change applied to avoid changing the current navigation route before submission.

### 4. CSP Allows `unsafe-inline`

File:

```text
apps/core/middleware.py
```

Current CSP allows inline scripts and styles because the project uses Tailwind CDN, Alpine attributes, and inline template behavior.

Why it matters:

Inline scripts/styles reduce CSP strength.

Suggested fix:

For production, move scripts/styles into static files and use nonce-based or hash-based CSP.

Change applied:

- No behavior change applied because the current UI depends on CDN and inline behavior.

### 5. `.env.example` Contains A Sample Password

File:

```text
.env.example
```

It contains a placeholder database password.

Why it matters:

It is okay for an example file, but never use example passwords in production.

Suggested fix:

Use a strong local or production password in your real `.env`.

Change applied:

- No code change needed.

## Security Strengths Found

- Custom user model uses Django auth.
- Password hashing is handled by Django.
- CSRF middleware is enabled.
- POST forms include CSRF tokens.
- Sessions are HTTP-only.
- Most pages require login.
- Household-owned objects are filtered by active household.
- Role checks protect editing features.
- ORM is used instead of raw SQL.
- Templates use normal escaped output.
- API endpoints require authentication.
- JWT endpoints are available for API clients.
- AI keys are read from environment variables.
- AI logs avoid raw prompt/response storage.
- Security headers middleware exists.
- Production security settings are environment driven.

## What To Say In Viva

Short answer:

"The project uses Django authentication for login and password hashing. Most views use `@login_required`, and household data is protected by filtering queries with the active household. Forms use CSRF tokens and Django validation. The project uses the ORM instead of raw SQL, which helps prevent SQL injection. API endpoints require authentication through session auth or JWT."

## Production Checklist

Before real deployment:

- Set `DEBUG=False`.
- Set a strong `SECRET_KEY`.
- Set correct `ALLOWED_HOSTS`.
- Set `CSRF_TRUSTED_ORIGINS`.
- Use HTTPS.
- Keep `SESSION_COOKIE_SECURE=True`.
- Keep `CSRF_COOKIE_SECURE=True`.
- Use a strong database password.
- Do not commit `.env`.
- Review CSP and remove `unsafe-inline` if possible.
- Convert logout to POST-only.
- Run:

```bash
python manage.py check --deploy
```
