from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    "group-1-madhumitha.onrender.com",
    "TalentLink-frontenddomain.com",
    "localhost",  # optional, for local testing
    "127.0.0.1"   # optional
]


DATABASES = {
    "default": dj_database_url.config(
        default=os.environ.get("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True,
    )
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

CORS_ALLOWED_ORIGINS = os.environ.get(
    "CORS_ALLOWED_ORIGINS"
).split(",")
