from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Crear el engine (motor de conexión a la DB)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica que la conexión esté viva antes de usarla
    echo=True  # Muestra las queries SQL en consola (útil para desarrollo)
)

# SessionLocal: cada instancia es una sesión de DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: clase base para todos los modelos
Base = declarative_base()

# Dependency para obtener la sesión de DB en los endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()