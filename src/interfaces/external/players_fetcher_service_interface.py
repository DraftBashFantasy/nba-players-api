from abc import ABC, abstractmethod
from domain.entities import GamelogEntity
from domain.entities.player_entity import PlayerEntity


class IPlayersFetcher(ABC):
    """
    Interface for gamelogs fetcher
    """

    @abstractmethod
    def fetch_new_player_data(self) -> list[PlayerEntity]:
        pass