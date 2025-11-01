from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# Crear el engine
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=settings.DEBUG)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base moderna con mejor type checking
class Base(DeclarativeBase):
    pass


# Dependency para obtener la sesión de DB
def get_db() -> Generator[Session, Any, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
