from abc import ABC, abstractmethod
from domain.entities.gamelog_entity import GamelogEntity


class IGamelogRepository(ABC):
    """
    Interface for gamelog repository.
    """

    @abstractmethod
    def upsert_many(self, gamelogs: list[GamelogEntity]) -> dict:
        pass

    @abstractmethod
    def get_all(self) -> list[GamelogEntity]:
        pass
