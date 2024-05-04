from abc import ABC, abstractmethod
from src.domain.entities import PlayerEntity


class IPlayersFetcher(ABC):
    """
    Interface for gamelogs fetcher
    """

    @abstractmethod
    def execute(self) -> list[PlayerEntity]:
        pass
