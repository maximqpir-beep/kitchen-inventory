"""Настройки локального учебного Django-проекта."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "django-insecure-local-kitchen-inventory-practice",
)
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "[::1]"]
INSTALLED_APPS = [
    "django.contrib.staticfiles", "homepage.apps.HomepageConfig",
    "items.apps.ItemsConfig", "movements.apps.MovementsConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kitchen_site.middleware.DataErrorMiddleware",
]
ROOT_URLCONF = "kitchen_site.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",
        ],
    },
}]
WSGI_APPLICATION = "kitchen_site.wsgi.application"
ASGI_APPLICATION = "kitchen_site.asgi.application"
DATABASES = {}
LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
INVENTORY_PATH = BASE_DIR / "data" / "inventory.json"
