from .base import *

DEBUG = True

ALLOWED_HOSTS = [
    "group-1-madhumitha.onrender.com",
    "TalentLink-frontenddomain.com",
    "localhost",  # optional, for local testing
    "127.0.0.1"   # optional
]


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "demo",
        "USER": "postgres",
        "PASSWORD": "madhumitha@81",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

CORS_ALLOW_ALL_ORIGINS = True
