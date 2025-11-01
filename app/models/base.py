from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.database import Base
from typing import Optional


class BaseModel(Base):
    __abstract__ = True  # Indica que esta clase no crea tabla propia

    # UUID como primary key
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)

    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(default=None)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )

    @property
    def is_deleted(self):
        return self.deleted_at is not None
