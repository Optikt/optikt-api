from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.config import settings
from app.core.security import create_access_token
from app.crud import user as crud_user
from app.database import get_db
from app.models.user import User
from app.schemas.access_token import AccessTokenData
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login.
    Recibe username y password, devuelve token JWT.
    """
    user = crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data=AccessTokenData(sub=user.id),  # "sub" es el subject (user_id)
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, db: Session = Depends(get_db)) -> Any:
    """
    Registrar nuevo usuario.

    TODO: Ahora es público, hay que restringirlo a admins.
    """
    # Verificar que el email no exista
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado",
        )

    # Verificar que el username no exista
    user = crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El username ya está en uso"
        )

    # Crear usuario
    user = crud_user.create(db, obj_in=user_in)

    return user


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)) -> Any:
    """
    Obtener información del usuario actual (desde el token).
    """
    return current_user
