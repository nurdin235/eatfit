import os
import sys
from datetime import timedelta
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
IS_TESTING = 'test' in sys.argv

# Small helpers keep environment-variable parsing readable below.
def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}

def env_int(name, default):
    value = os.environ.get(name)
    if value in (None, ''):
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(f"{name} must be an integer.") from exc

def env_list(name, default=''):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]

def vercel_hosts():
    hosts = []
    for name in ('VERCEL_URL', 'VERCEL_BRANCH_URL', 'VERCEL_PROJECT_PRODUCTION_URL'):
        value = os.environ.get(name)
        if value:
            hosts.append(value.removeprefix('https://').removeprefix('http://').strip('/'))
    return hosts

def https_origins(hosts):
    return [f"https://{host}" for host in hosts if host]

DEBUG = env_bool('DEBUG', False)

# In production, SECRET_KEY must be configured. The random fallback is only for
# local development because it changes whenever the process restarts.
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = get_random_secret_key()
    else:
        raise ImproperlyConfigured("Set SECRET_KEY before running EatFit with DEBUG=False.")

VERCEL_HOSTS = vercel_hosts()
ALLOWED_HOSTS = env_list('ALLOWED_HOSTS', 'localhost,127.0.0.1,testserver') + VERCEL_HOSTS
CSRF_TRUSTED_ORIGINS = (
    env_list('CSRF_TRUSTED_ORIGINS', 'http://localhost:8000,http://127.0.0.1:8000')
    + https_origins(VERCEL_HOSTS)
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    
    # Local Django apps. Each app owns one feature area of EatFit.
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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('SUPABASE_DATABASE_URL')
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_SSL_DEFAULT = bool(DATABASE_URL) or DB_HOST not in {'', 'localhost', '127.0.0.1'}
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=env_int('DB_CONN_MAX_AGE', 0),
            ssl_require=env_bool('DB_SSL_REQUIRE', DB_SSL_DEFAULT),
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'eatfitsdb'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': DB_HOST,
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': env_int('DB_CONN_MAX_AGE', 0),
        }
    }

if env_bool('DB_SSL_REQUIRE', DB_SSL_DEFAULT):
    DATABASES['default'].setdefault('OPTIONS', {})['sslmode'] = 'require'

# Supabase's transaction pooler and other PgBouncer-style poolers do not support
# Django server-side cursors safely.
DATABASES['default']['DISABLE_SERVER_SIDE_CURSORS'] = env_bool('DB_DISABLE_SERVER_SIDE_CURSORS', True)

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': env_int('PASSWORD_MIN_LENGTH', 12)},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.ScryptPasswordHasher',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.environ.get('TIME_ZONE', 'Africa/Douala')
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE_BACKEND = os.environ.get('STATICFILES_STORAGE_BACKEND')
if not STATICFILES_STORAGE_BACKEND:
    use_manifest_static = env_bool('USE_MANIFEST_STATIC', bool(os.environ.get('VERCEL')) and not IS_TESTING)
    STATICFILES_STORAGE_BACKEND = (
        'whitenoise.storage.CompressedManifestStaticFilesStorage'
        if use_manifest_static
        else 'whitenoise.storage.CompressedStaticFilesStorage'
    )
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': STATICFILES_STORAGE_BACKEND},
}
WHITENOISE_MANIFEST_STRICT = env_bool('WHITENOISE_MANIFEST_STRICT', False)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# This tells Django to use apps.users.models.User instead of the built-in User.
AUTH_USER_MODEL = 'users.User'

LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'auth:login'

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-5.2')
AI_DAILY_LIMIT = int(os.environ.get('AI_DAILY_LIMIT', '25'))

# REST Framework
REST_FRAMEWORK = {
    # DRF accepts normal logged-in browser sessions and JWT tokens for API clients.
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': os.environ.get('DRF_ANON_RATE', '100/day'),
        'user': os.environ.get('DRF_USER_RATE', '1000/day'),
        'ai_recommendations': f'{AI_DAILY_LIMIT}/day',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env_int('JWT_ACCESS_MINUTES', 15)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env_int('JWT_REFRESH_DAYS', 1)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Celery
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

# These security settings become stricter automatically when DEBUG=False.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = env_bool('USE_X_FORWARDED_HOST', bool(VERCEL_HOSTS))
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)
SESSION_COOKIE_SAMESITE = os.environ.get('SESSION_COOKIE_SAMESITE', 'Lax')
CSRF_COOKIE_SAMESITE = os.environ.get('CSRF_COOKIE_SAMESITE', 'Lax')
SESSION_COOKIE_AGE = env_int('SESSION_COOKIE_AGE', 60 * 60 * 24 * 14)
SESSION_SAVE_EVERY_REQUEST = env_bool('SESSION_SAVE_EVERY_REQUEST', False)
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False if DEBUG else True)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0' if DEBUG else '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', not DEBUG)
SECURE_HSTS_PRELOAD = env_bool('SECURE_HSTS_PRELOAD', not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = os.environ.get('SECURE_REFERRER_POLICY', 'same-origin')
SECURE_CROSS_ORIGIN_OPENER_POLICY = os.environ.get('SECURE_CROSS_ORIGIN_OPENER_POLICY', 'same-origin')
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = env_bool('CSRF_COOKIE_HTTPONLY', True)
CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'
DATA_UPLOAD_MAX_MEMORY_SIZE = env_int('DATA_UPLOAD_MAX_MEMORY_SIZE', 1024 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = env_int('FILE_UPLOAD_MAX_MEMORY_SIZE', 1024 * 1024)
DATA_UPLOAD_MAX_NUMBER_FIELDS = env_int('DATA_UPLOAD_MAX_NUMBER_FIELDS', 500)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list('CORS_ALLOWED_ORIGINS', '')
CORS_ALLOW_CREDENTIALS = env_bool('CORS_ALLOW_CREDENTIALS', False)
CONTENT_SECURITY_POLICY = os.environ.get(
    'CONTENT_SECURITY_POLICY',
    "default-src 'self'; "
    "base-uri 'self'; "
    "object-src 'none'; "
    "script-src 'self' https://cdn.jsdelivr.net; "
    "style-src 'self'; "
    "img-src 'self' data: https://ui-avatars.com; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none';",
)
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/').strip() or 'admin/'
if not ADMIN_URL.endswith('/'):
    ADMIN_URL = f'{ADMIN_URL}/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'django.security': {'handlers': ['console'], 'level': 'WARNING'},
        'apps': {'handlers': ['console'], 'level': os.environ.get('APP_LOG_LEVEL', 'INFO')},
    },
}
