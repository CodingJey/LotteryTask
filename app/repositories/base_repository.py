from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Generic, TypeVar, Type, List, Optional, Any
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Generic base repository for CRUD operations."""
    def __init__(self, session: Session, model: Type[ModelType]):
        self.session = session
        self.model = model

    def get(self, pk : Any) -> Optional[ModelType]:
        return self.session.get(self.model, pk)

    def list_all(self) -> List[ModelType]:
        result = self.session.execute(select(self.model))
        return result.scalars().all()

    def _refresh(self, obj: ModelType) -> ModelType:
        self.session.refresh(obj)
        return obj