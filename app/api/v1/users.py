from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_current_superuser
from app.crud.user import user as crud_user
from app.database import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(dependencies=[])


@router.get("/", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Security(get_current_active_user),
):
    """
    Listar todos los usuarios.
    Solo usuarios activos pueden ver la lista.
    """
    return crud_user.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=UserResponse)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    Obtener información del usuario actual.
    """
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Obtener usuario por ID.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Solo el mismo usuario o admin/superuser pueden ver detalles
    if user.id != current_user.id:
        if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver este usuario",
            )

    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    # Solo superuser puede crear
    current_user: User = Depends(get_current_superuser),
):
    """
    Crear nuevo usuario.
    Solo super usuarios pueden crear usuarios.
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


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Actualizar usuario.
    Los usuarios pueden actualizarse a sí mismos.
    Solo admin/superuser pueden actualizar a otros.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Verificar permisos
    if user.id != current_user.id:
        if current_user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para actualizar este usuario",
            )

    # Si intenta cambiar el rol, solo superuser puede
    if user_in.role and user_in.role != user.role:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo super usuarios pueden cambiar roles",
            )

    # Verificar email único si se está cambiando
    if user_in.email and user_in.email != user.email:
        existing_user = crud_user.get_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está en uso",
            )

    # Verificar username único si se está cambiando
    if user_in.username and user_in.username != user.username:
        existing_user = crud_user.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El username ya está en uso",
            )

    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    # Solo superuser puede eliminar
    current_user: User = Depends(get_current_superuser),
) -> Any:
    """
    Eliminar usuario (soft delete).
    Solo super usuarios pueden eliminar usuarios.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # No permitir auto-eliminación
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminarte a ti mismo",
        )

    user = crud_user.soft_delete(db, id=user_id)
    return user
