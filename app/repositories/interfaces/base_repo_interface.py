from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic, Any

ModelType = TypeVar('ModelType')


class BaseRepositoryInterface(Generic[ModelType], ABC):
    """
    Interface for common repository operations.
    Specific repository interfaces can choose to inherit from this
    or define these methods explicitly if preferred for clarity.
    """
    @abstractmethod
    def get(self, pk: Any) -> Optional[ModelType]:
        """Retrieve an entity by its primary key."""
        pass

    @abstractmethod
    def list_all(self) -> List[ModelType]:
        """List all entities of this type."""
        pass