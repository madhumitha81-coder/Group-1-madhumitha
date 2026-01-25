
import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# SECURITY / DEBUG
# =========================
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"  # True for local dev

# =========================
# TRUST RENDER PROXY
# =========================
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# =========================
# ALLOWED HOSTS
# =========================
if DEBUG:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
else:
    ALLOWED_HOSTS = ["group-1-madhumitha.onrender.com", ".onrender.com"]

# =========================
# CSRF TRUSTED ORIGINS
# =========================
if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "https://group-1-madhumitha.onrender.com",
        "https://*.onrender.com"
    ]

# =========================
# DATABASE CONFIG
# =========================
DATABASE_URL = os.environ.get("DATABASE_URL")

if DEBUG:
    # Local development
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://postgres:madhumitha%4081@localhost:5432/demo",
            conn_max_age=600,
            ssl_require=False,  # Local DB does NOT use SSL
        )
    }
else:
    # Production (Render)
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,   # Must be set in Render Environment
            conn_max_age=600,
            ssl_require=True,       # Render requires SSL
        )
    }

# =========================
# HTTPS / SECURITY
# =========================
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# =========================
# COOKIE SETTINGS
# =========================
# =========================
# HTTPS / SECURITY
# =========================
if not DEBUG:
    # Trust Render's HTTPS proxy
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    USE_X_FORWARDED_HOST = True

    # Only redirect if request is HTTP externally
    SECURE_SSL_REDIRECT = True

    # Cookies over HTTPS
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

SESSION_COOKIE_DOMAIN = None
CSRF_COOKIE_DOMAIN = None

    
# =========================
# FRONTEND TOKEN
# =========================
FRONTEND_ACCESS_TOKEN = os.environ.get("FRONTEND_ACCESS_TOKEN", "dev-token")

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
# CORS CONFIG
# =========================
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    cors_origins = os.environ.get("CORS_ALLOWED_ORIGINS")
    if cors_origins:
        CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(",")]
    else:
        CORS_ALLOWED_ORIGINS = ["https://group-1-madhumitha.onrender.com"]

# =========================
# MIDDLEWARE
# =========================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
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
# TIMEZONE & LANGUAGE
# =========================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# =========================
# LOGGING
# =========================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "ERROR"},
}

# =========================
# DEBUG INFO
# =========================
if DEBUG:
    print("DEBUG:", DEBUG)
    print("ALLOWED_HOSTS:", ALLOWED_HOSTS)
    print("Database NAME:", DATABASES["default"].get("NAME"))
