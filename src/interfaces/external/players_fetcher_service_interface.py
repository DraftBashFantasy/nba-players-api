from abc import ABC, abstractmethod
from src.domain.entities import PlayerEntity


class IPlayersFetcher(ABC):
    """
    Interface for gamelogs fetcher
    """

    @abstractmethod
    def fetch_new_player_data(self) -> list[PlayerEntity]:
        pass
