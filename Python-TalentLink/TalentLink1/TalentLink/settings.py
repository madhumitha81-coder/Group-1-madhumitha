import os
from pathlib import Path
import dj_database_url

# =========================
# BASE DIR
# =========================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# FRONTEND ACCESS TOKEN
# =========================
FRONTEND_ACCESS_TOKEN = os.environ.get("FRONTEND_ACCESS_TOKEN", "dev-token")

# =========================
# SECURITY
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"



# ALLOWED_HOSTS for Django deployment on Render
ALLOWED_HOSTS = os.environ.get(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1"
).split(",")



# =========================
# DATABASE CONFIG
# =========================
LOCAL_DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'demo',
    'USER': 'postgres',
    'PASSWORD': 'madhumitha@81',
    'HOST': 'localhost',
    'PORT': '5432',
}

DATABASES = {
    "default": dj_database_url.config(
        default=f"postgres://{LOCAL_DATABASE['USER']}:{LOCAL_DATABASE['PASSWORD']}@{LOCAL_DATABASE['HOST']}:{LOCAL_DATABASE['PORT']}/{LOCAL_DATABASE['NAME']}",
        conn_max_age=600,
    )
}

# Use SSL in production only
if not DEBUG:
    DATABASES['default']['OPTIONS'] = {'sslmode': 'require'}
else:
    DATABASES['default']['OPTIONS'] = {'sslmode': 'disable'}  # <-- important for local dev

# =========================
# INSTALLED APPS
# =========================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_filters",
    "rest_framework",
    "corsheaders",
    "rest_framework.authtoken",
    "myapp.apps.MyappConfig",
]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "myapp.middleware.VerifyFrontendTokenMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# =========================
# URLS & TEMPLATES
# =========================
ROOT_URLCONF = "TalentLink.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "myapp" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "TalentLink.wsgi.application"

# =========================
# STATIC & MEDIA
# =========================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# =========================
# AUTH
# =========================
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# =========================
# REST FRAMEWORK
# =========================
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}

# =========================
# CORS
# =========================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = os.environ.get(
        "CORS_ALLOWED_ORIGINS", "https://TalentLink-frontenddomain.com"
    ).split(",")

# =========================
# HTTPS / SECURITY
# =========================
SECURE_SSL_REDIRECT = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# =========================
# TIMEZONE & LANGUAGE
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# =========================
# DEBUG: Print database
# =========================
print("Using database:", DATABASES['default'].get('NAME'))
