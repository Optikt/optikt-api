from datetime import timezone, datetime
from typing import Generic, TypeVar, Type, Optional, List, Any
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy.orm import Session
from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _update_db_obj(self, db: Session, obj: ModelType) -> None:
        """Helper para commit y refresh de objetos"""
        db.add(obj)
        db.commit()
        db.refresh(obj)

    def get(
        self, db: Session, id: Any, include_deleted: bool = False
    ) -> Optional[ModelType]:
        """Obtener un registro por ID"""
        query = db.query(self.model).filter(self.model.id == id)
        if not include_deleted:
            query = query.filter(self.model.deleted_at.is_(None))
        return query.first()

    def get_multi(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ModelType]:
        """Obtener múltiples registros"""
        query = db.query(self.model)
        if not include_deleted:
            query = query.filter(self.model.deleted_at.is_(None))
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        """Crear un nuevo registro"""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self._update_db_obj(db, db_obj)
        return db_obj

    def update(
        self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar un registro existente"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self._update_db_obj(db, db_obj)
        return db_obj

    def soft_delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """Soft delete: marca como eliminado sin borrar"""
        obj = self.get(db, id)
        if obj:
            obj.deleted_at = datetime.now(timezone.utc)
            self._update_db_obj(db, obj)
        return obj

    def hard_delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """Hard delete: elimina permanentemente de la DB"""
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
