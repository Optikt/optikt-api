from typing import Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return (
            db.query(User)
            .filter(User.email == email, User.deleted_at.is_(None))
            .first()
        )

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Obtener usuario por username"""
        return (
            db.query(User)
            .filter(User.username == username, User.deleted_at.is_(None))
            .first()
        )

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Crear usuario con password hashed"""
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            full_name=obj_in.full_name,
            hashed_password=get_password_hash(obj_in.password),
            role=obj_in.role.value,
            is_active=True,
            is_superuser=False,
        )
        self._update_db_obj(db, db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """Actualizar usuario, hace hash del password si se proporciona"""
        update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        if "role" in update_data:
            update_data["role"] = update_data["role"].value

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        self._update_db_obj(db, db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Autenticar usuario (usado en login)"""
        user = self.get_by_username(db, username)
        if not user:
            return None
        if not user.is_active:
            return None

        # Si `verify_password` es true, se retorna el user, si no None
        return user if verify_password(password, user.hashed_password) else None


# Instancia única para usar en los endpoints
user = CRUDUser(User)
