from abc import ABC, abstractmethod
from src.domain.entities import ProjectionEntity


class IProjectionRepository(ABC):
    """
    Interface for Projections Repository.
    """

    @abstractmethod
    def upsert_many(self, projections: list[ProjectionEntity]) -> None:
        pass