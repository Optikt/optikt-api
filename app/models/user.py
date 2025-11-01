from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel
from app.models.enums import UserRole


class User(BaseModel):
    __tablename__ = "users"

    # Con Mapped, el type checker entiende los tipos correctamente
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    role: Mapped[str] = mapped_column(default=UserRole.SELLER.value)
