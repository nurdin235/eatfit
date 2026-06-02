# EatFit Security Checklist

## Current OWASP Top 10 Coverage

- A01 Broken Access Control: household data is filtered by active household; write views now require owner/editor roles; cross-household meal plan access is tested.
- A02 Cryptographic Failures: production requires a real `SECRET_KEY`; new passwords use Argon2; cookies are secure, HTTP-only where appropriate, and SameSite Lax.
- A03 Injection: database access uses Django ORM and serializers; no raw SQL or user-controlled command execution is present.
- A04 Insecure Design: AI is advisory only, allergies/dislikes are filtered server-side before model ranking, and AI output cannot select records outside server-filtered candidates.
- A05 Security Misconfiguration: deploy checks run with `--deploy --fail-level WARNING`; security headers, SSL redirect, HSTS, CSP, and strict host/CSRF settings are configured.
- A06 Vulnerable And Outdated Components: Django is on 5.2 LTS; npm audit and `pip-audit -r requirements.txt` pass.
- A07 Identification And Authentication Failures: login/register are rate-limited; logout is POST-only; password minimum length is 12; JWT access tokens are short-lived with refresh rotation.
- A08 Software And Data Integrity Failures: dependencies are pinned; CDN use is reduced; remaining HTMX CDN script is version-pinned with SRI.
- A09 Security Logging And Monitoring Failures: Django security warnings log to console; AI interactions store hashes/summaries instead of raw prompt/response bodies.
- A10 Server-Side Request Forgery: no user-controlled outbound URL fetching exists in the current app.

## Django Controls

- CSRF middleware is enabled and forms include `{% csrf_token %}`.
- `SecurityHeadersMiddleware` sets CSP, Referrer-Policy, Permissions-Policy, and cross-domain restrictions.
- Production flags are environment-controlled: `SECURE_SSL_REDIRECT`, secure cookies, HSTS, preload, and proxy SSL header.
- `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `SECRET_KEY`, and database credentials are environment-driven.
- Upload/post limits are set with `DATA_UPLOAD_MAX_MEMORY_SIZE`, `FILE_UPLOAD_MAX_MEMORY_SIZE`, and `DATA_UPLOAD_MAX_NUMBER_FIELDS`.
- User-generated content is rendered escaped by Django templates.

## Supabase And Vercel Controls

- `DATABASE_URL` supports Supabase transaction pooler URLs.
- SSL is required for remote/Supabase database hosts.
- Server-side cursors are disabled for pooler compatibility.
- Vercel build can run migrations and `seed_eatfit` after credentials are supplied.
- `.gitignore` and `.vercelignore` exclude `.env`, local databases, generated artifacts, and non-runtime resources.

## AI / LLM Controls

- OpenAI API keys stay server-side only.
- Prompts minimize data to preferences and recipe candidates.
- Allergy/diet filtering runs before AI recommendation ranking.
- Structured JSON output is requested from OpenAI.
- AI ranking IDs are hydrated only from eligible server-side candidates.
- AI output text and numeric values are clipped/normalized before storage.
- Raw prompts and raw responses are not stored.
- Daily AI recommendation rate limiting is configured with `AI_DAILY_LIMIT`.
- Local fallback keeps demos and core planning functional without OpenAI.

## Remaining Operational Duties

- Set a 50+ character random `SECRET_KEY` in Vercel.
- Keep Vercel, Supabase, Python, npm, and OpenAI SDK dependencies patched.
- Enable Vercel platform protections such as WAF/bot protection if this becomes public-facing.
- Review Supabase database roles and never expose database passwords in browser code.
- No system can be guaranteed impossible to hack; treat this checklist as hardening, not a permanent proof of security.
