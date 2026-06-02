# 12. Final Submission Checklist

Use this checklist before submitting EatFit.

## Source Code

- [ ] Source code folder is ready.
- [ ] `apps/` folder is included.
- [ ] `config/` folder is included.
- [ ] `templates/` folder is included.
- [ ] `static/` folder is included, even if currently empty.
- [ ] `docker/` folder is included if Docker support is part of submission.
- [ ] `manage.py` is included.
- [ ] No important app file has been deleted.

## Documentation

- [ ] `README.md` is included.
- [ ] `docs/` folder is included.
- [ ] `docs/01_PROJECT_OVERVIEW.md` is included.
- [ ] `docs/02_DJANGO_ARCHITECTURE_EXPLAINED.md` is included.
- [ ] `docs/03_FOLDER_AND_FILE_STRUCTURE.md` is included.
- [ ] `docs/04_DATABASE_AND_MODELS_EXPLAINED.md` is included.
- [ ] `docs/05_URLS_VIEWS_TEMPLATES_FLOW.md` is included.
- [ ] `docs/06_FORMS_VALIDATION_AND_DATA_SAVING.md` is included.
- [ ] `docs/07_AUTHENTICATION_AUTHORIZATION_AND_SECURITY.md` is included.
- [ ] `docs/08_STEP_BY_STEP_REBUILD_GUIDE.md` is included.
- [ ] `docs/09_FUNCTIONALITIES_EXPLAINED.md` is included.
- [ ] `docs/10_HOW_TO_RUN_TEST_AND_SUBMIT.md` is included.
- [ ] `docs/11_BEGINNER_VIVA_AND_PRESENTATION_GUIDE.md` is included.
- [ ] `docs/12_FINAL_SUBMISSION_CHECKLIST.md` is included.
- [ ] Existing docs such as architecture/API/security diagrams are still included if useful.

## Dependencies

- [ ] `requirements.txt` is included.
- [ ] Dependencies install successfully with `pip install -r requirements.txt`.
- [ ] Virtual environment folder is excluded.
- [ ] No local package cache is included.

## Environment And Secrets

- [ ] `.env.example` is included.
- [ ] Real `.env` is excluded from final ZIP or Git submission.
- [ ] Real database password is not exposed.
- [ ] Real `SECRET_KEY` is not exposed.
- [ ] OpenAI API key is not exposed.
- [ ] Any private credentials are removed from screenshots.

## Database And Migrations

- [ ] Migration files are included.
- [ ] `python manage.py makemigrations --check` passes or documented if blocked.
- [ ] `python manage.py migrate` runs on a clean database.
- [ ] Database configuration is explained.
- [ ] PostgreSQL setup instructions are included.
- [ ] `db.sqlite3` is understood as not active under current PostgreSQL settings.

## Admin Panel

- [ ] `python manage.py createsuperuser` works.
- [ ] `/admin/` opens.
- [ ] Superuser can log in.
- [ ] User model appears in admin.
- [ ] Recipe models appear in admin.
- [ ] Meal models appear in admin.
- [ ] Grocery models appear in admin.
- [ ] Pantry models appear in admin.
- [ ] Notification models appear in admin.

## Authentication

- [ ] Registration tested.
- [ ] Login tested.
- [ ] Logout tested.
- [ ] Incorrect login tested.
- [ ] Password hashing explained.
- [ ] Session behavior explained.

## Authorization

- [ ] Anonymous user is redirected from dashboard to login.
- [ ] Household filtering tested.
- [ ] Cross-household access blocked or explained by tests.
- [ ] Owner can add household member.
- [ ] Non-owner restriction is understood.
- [ ] Editor role behavior is explained.

## CRUD Features

- [ ] Recipe create tested.
- [ ] Recipe list tested.
- [ ] Recipe search tested.
- [ ] Recipe detail tested.
- [ ] Recipe edit tested.
- [ ] Recipe delete tested.
- [ ] Meal plan create tested.
- [ ] Meal plan list tested.
- [ ] Add/replace meal tested.
- [ ] Delete meal tested.
- [ ] Analyze meal tested.
- [ ] Grocery generation tested.
- [ ] Grocery item edit tested.
- [ ] Grocery purchased toggle tested.
- [ ] Pantry add tested.
- [ ] Pantry list tested.
- [ ] Pantry edit tested.
- [ ] Pantry delete tested.
- [ ] Notification preferences tested.
- [ ] Mark notification read tested.

## Forms

- [ ] Registration form validation tested.
- [ ] Duplicate email validation tested.
- [ ] Login form validation tested.
- [ ] Profile form saving tested.
- [ ] Meal plan date validation tested.
- [ ] Meal form recipe/custom validation tested.
- [ ] Recipe form and ingredient formset tested.
- [ ] Pantry form tested.
- [ ] Grocery item form tested.
- [ ] Notification preference form tested.
- [ ] CSRF token exists in POST templates.

## Security

- [ ] `DEBUG=False` is documented for production.
- [ ] `SECRET_KEY` handling is explained.
- [ ] `ALLOWED_HOSTS` handling is explained.
- [ ] CSRF usage is explained.
- [ ] Password hashing is explained.
- [ ] Session management is explained.
- [ ] `login_required` usage is explained.
- [ ] Input validation is explained.
- [ ] ORM protection against SQL injection is explained.
- [ ] Template escaping against XSS is explained.
- [ ] Security headers are explained.
- [ ] Logout GET weakness is documented.
- [ ] File upload absence is documented.
- [ ] API authentication is explained.

## API

- [ ] JWT token endpoint documented.
- [ ] User API documented.
- [ ] Recipes API documented.
- [ ] Meal plans API documented.
- [ ] Grocery generation API documented.
- [ ] Notifications API documented.
- [ ] AI recommendations API documented.
- [ ] API authentication explained.

## Tests And Checks

- [ ] `python manage.py check` run.
- [ ] `python manage.py makemigrations --check` run.
- [ ] `python manage.py test` run if database is available.
- [ ] Development server start verified.
- [ ] Any errors are documented clearly.
- [ ] Manual browser testing completed.

## Screenshots

- [ ] Login page screenshot.
- [ ] Register page screenshot.
- [ ] Dashboard screenshot.
- [ ] Profile page screenshot.
- [ ] Household page screenshot.
- [ ] Recipes list screenshot.
- [ ] Recipe detail screenshot.
- [ ] Recipe form screenshot.
- [ ] Meal plans list screenshot.
- [ ] Meal plan detail screenshot.
- [ ] Custom meal analysis screenshot.
- [ ] Grocery list screenshot.
- [ ] Pantry page screenshot.
- [ ] Nutrition page screenshot.
- [ ] Budget page screenshot.
- [ ] Notifications page screenshot.
- [ ] Admin panel screenshot.

## Report And Presentation

- [ ] Project title included.
- [ ] Problem statement included.
- [ ] Objectives included.
- [ ] Tools and technologies included.
- [ ] System architecture included.
- [ ] Database design included.
- [ ] Screenshots included.
- [ ] Security explanation included.
- [ ] Testing explanation included.
- [ ] Limitations included.
- [ ] Future improvements included.
- [ ] Viva script reviewed.

## Git Or ZIP Preparation

- [ ] Git repository is clean if using Git.
- [ ] `.gitignore` excludes `.env`, `.venv`, `venv`, `__pycache__`, `.pyc`, and local secrets.
- [ ] Final ZIP prepared.
- [ ] ZIP opens correctly.
- [ ] ZIP contains README and docs.
- [ ] ZIP does not contain real `.env`.
- [ ] ZIP does not contain virtual environment.

## Final Commands To Run

Run:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test
python manage.py runserver
```

If all are successful, the project is in strong submission shape.

If any command fails, write down:

- command run
- error message
- likely cause
- fix attempted

## What To Read First Before Viva

Read in this order:

1. `README.md`
2. `docs/01_PROJECT_OVERVIEW.md`
3. `docs/02_DJANGO_ARCHITECTURE_EXPLAINED.md`
4. `docs/05_URLS_VIEWS_TEMPLATES_FLOW.md`
5. `docs/06_FORMS_VALIDATION_AND_DATA_SAVING.md`
6. `docs/07_AUTHENTICATION_AUTHORIZATION_AND_SECURITY.md`
7. `docs/11_BEGINNER_VIVA_AND_PRESENTATION_GUIDE.md`

## Final Confidence Check

You should be able to answer:

- What is this project?
- What problem does it solve?
- What is Django?
- What is a Django project?
- What is a Django app?
- What is MTV?
- How does a URL reach a view?
- How does a form save to the database?
- How does login work?
- How is household data protected?
- What are the main models?
- What are migrations?
- What does admin do?
- What security features are used?
- What would you improve next?

If you can answer these, you are ready to present.
