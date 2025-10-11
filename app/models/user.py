from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel
from app.models.enums import UserRole

class User(BaseModel):
    __tablename__ = "users"
    
    # Información básica
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Estado y permisos
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Role como Enum
    role = Column(String, nullable=False, default=UserRole.SELLER.value)