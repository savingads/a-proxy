"""
Database repositories package.

This package provides the data access layer with repository pattern implementation.
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Any


class BaseRepository(ABC):
    """Abstract base class for all repositories."""

    @abstractmethod
    def get(self, id: int) -> Optional[Any]:
        """Get entity by ID."""

    @abstractmethod
    def get_all(self, **filters) -> List[Any]:
        """Get all entities with optional filtering."""

    @abstractmethod
    def save(self, entity: Any) -> int:
        """Save entity and return ID."""

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete entity by ID."""


# Import repository implementations
from .persona import PersonaRepository
from .journey import JourneyRepository
from .archive import ArchiveRepository
from .user import UserRepository
from .settings import SettingsRepository

__all__ = [
    'BaseRepository',
    'PersonaRepository',
    'JourneyRepository',
    'ArchiveRepository',
    'UserRepository',
    'SettingsRepository',
]
