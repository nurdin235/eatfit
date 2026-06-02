# Vercel + Supabase Deployment

EatFit is configured for Vercel serverless Python with Supabase PostgreSQL.

## Required Vercel Environment Variables

Set these in Vercel Project Settings -> Environment Variables:

```text
DEBUG=False
SECRET_KEY=<generate a long random secret, 50+ characters>
DATABASE_URL=<Supabase transaction pooler connection string>
RUN_DEPLOY_MIGRATIONS=True
RUN_DEPLOY_SEED=True
RUN_DEPLOY_CHECKS=True
OPENAI_API_KEY=<optional, server-side only>
```

For custom domains, also set:

```text
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
CORS_ALLOWED_ORIGINS=
```

Vercel deployment URLs are detected automatically from `VERCEL_URL`.

## Supabase Connection

Use Supabase's transaction pooler URL for Vercel/serverless. It usually looks like:

```text
postgresql://postgres.PROJECT_REF:YOUR_DB_PASSWORD@aws-REGION.pooler.supabase.com:6543/postgres?sslmode=require
```

The app also supports separate `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` variables, but `DATABASE_URL` is simpler and preferred.

## Build And Seed Flow

Vercel runs:

```text
npm run build:css && python scripts/vercel_build.py
```

The build helper:

- collects static files
- runs `python manage.py check --deploy --fail-level WARNING`
- runs migrations only when `RUN_DEPLOY_MIGRATIONS=True`
- runs `seed_eatfit` only when `RUN_DEPLOY_SEED=True`

The seed command is idempotent: it uses `update_or_create`, so repeated deploys update demo ingredients and recipes rather than duplicating them.

## Local Verification

```bash
npm run build:css
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
python -m pip check
python -m pip_audit -r requirements.txt
npm audit --audit-level=moderate
```

For a production-style local build check, temporarily provide a strong secret:

```powershell
$env:SECRET_KEY='replace-with-a-long-random-secret'
python scripts\vercel_build.py
Remove-Item Env:\SECRET_KEY
```

## Security Notes

No application can be guaranteed impossible to hack. EatFit now ships with stronger controls for the current OWASP Top 10 themes: access control, dependency integrity, secure configuration, SSRF avoidance, input limits, session and CSRF hardening, security headers, and AI-output bounds. Keep Vercel, Supabase, Python packages, and npm packages updated continuously.
