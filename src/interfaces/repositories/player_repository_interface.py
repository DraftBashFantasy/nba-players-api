from abc import ABC, abstractmethod
from src.domain.entities import PlayerEntity, ProjectionEntity


class IPlayerRepository(ABC):
    """
    Interface for Players Repository.
    """

    @abstractmethod
    def upsert_many_projections(self, projections: list[ProjectionEntity]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[PlayerEntity]:
        pass

    @abstractmethod
    def upsert_many(self, player: list[PlayerEntity]) -> None:
        pass
