from sqlalchemy.ext.asyncio import AsyncSession
from typing import Generic, TypeVar, Type, List # Correct import line
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
class BaseRepository(Generic[ModelType]):
    """Base repository class with database access."""
    def __init__(self, session: AsyncSession):        
        self.session = session
        self.model: Type[ModelType]