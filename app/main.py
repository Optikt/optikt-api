from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from fastapi import Depends
from sqlalchemy.orm import Session
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


# Ruta de prueba
@app.get("/")
def root():
    return {
        "message": "Bienvenido a Optikt API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Optikt API está ejecutándose"}


@app.get("/test-db")
def test_database(db: Session = Depends(get_db)):
    user_count = db.query(User).count()
    return {
        "status": "Database connected!",
        "users_count": user_count,
        "table": "users with UUID, soft delete, and timestamps"
    }