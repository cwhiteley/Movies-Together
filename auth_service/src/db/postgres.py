"""Модуль подключения БД"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from src.core.config import settings


db_uri = (
    "postgresql://"
    f"{settings.postgres_auth.user}:{settings.postgres_auth.password}@"
    f"{settings.postgres_auth.host}:{settings.postgres_auth.port}/"
    f"{settings.postgres_auth.dbname}"
)
db = create_engine(db_uri, convert_unicode=True)
Session = sessionmaker(bind=db, autocommit=False, autoflush=False)
db_session = scoped_session(Session)

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    from src.models import oauth_request  # noqa: F401
