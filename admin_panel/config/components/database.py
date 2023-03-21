from config.config import settings


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": settings.postgres_movies.dbname,
        "USER": settings.postgres_movies.user,
        "PASSWORD": settings.postgres_movies.password,
        "HOST": settings.postgres_movies.host,
        "PORT": settings.postgres_movies.port,
        "OPTIONS": {"options": "-c search_path=movies_content,public"},
    }
}
