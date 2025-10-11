from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

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
