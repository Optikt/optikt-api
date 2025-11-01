from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1 import auth, users
from app.config import settings
from app.database import get_db
from app.models import User

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configurar CORS para que tu frontend (SvelteKit) pueda comunicarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Puerto default de SvelteKit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir Auth router bajo /v1/auth
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])

# Incluir Auth router bajo /v1/users
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])


# Ruta de prueba
@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "Bienvenido a Optikt API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


# Health check
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Optikt API está ejecutándose"}


@app.get("/test-db")
def test_database(db: Session = Depends(get_db)) -> dict[str, str | int]:
    user_count = db.query(User).count()
    return {
        "status": "Database connected!",
        "users_count": user_count,
        "table": "users with UUID, soft delete, and timestamps",
    }
