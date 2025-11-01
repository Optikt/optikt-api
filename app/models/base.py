from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
from uuid import uuid4
from app.database import Base as SQLAlchemyBase


class BaseModel(SQLAlchemyBase):
    __abstract__ = True  # Indica que esta clase no crea tabla propia

    # UUID como primary key
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4, index=True)

    # Soft delete
    deleted_at = Column(DateTime, nullable=True, default=None)

    # TODO: Fix time date. .utcnow is deprecated
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    @property
    def is_deleted(self):
        return self.deleted_at is not None
