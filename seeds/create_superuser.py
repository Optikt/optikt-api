from uuid import uuid4

from app.core.security import get_password_hash
from app.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User


def create_superuser():
    db = SessionLocal()

    username = "optikt"

    if db.query(User).filter(User.username == username).first():
        print("❌ Superusuario ya existe")
        db.close()
        return

    password = "SuperAdmin_123"  # Cambiar luego

    # Crear superusuario
    superuser = User(
        id=uuid4(),
        email="optikt.vision@gmail.com",
        username=username,
        full_name="Optikt Administrador",
        hashed_password=get_password_hash(password),
        role=UserRole.SUPER_ADMIN.value,
        is_active=True,
        is_superuser=True,
    )

    db.add(superuser)
    db.commit()
    db.refresh(superuser)

    print("✅ Superusuario creado:")
    print(f"   Email: {superuser.email}")
    print(f"   Username: {superuser.username}")
    print(f"   Password: {password}")
    print(f"   Role: {superuser.role}")
    print("   Nota: Cambiar contraseña para seguridad")

    db.close()


if __name__ == "__main__":
    create_superuser()
