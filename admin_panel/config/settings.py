from pathlib import Path

from config.config import settings
from dotenv import load_dotenv
from split_settings.tools import include

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = settings.django.secret_key

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "django"]

include(
    "components/database.py",
    "components/installed_apps.py",
    "components/middleware.py",
    "components/templates.py",
    "components/auth_password_validators.py",
)

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOCALE_PATHS = ["movies/locale"]

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:8080",
]

CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]
