from abc import ABC, abstractmethod
from datetime import datetime
from src.domain.entities.gamelog_entity import GamelogEntity


class IGamelogRepository(ABC):
    """
    Interface for gamelog repository.
    """

    @abstractmethod
    def upsert_many(self, gamelogs: list[GamelogEntity]) -> dict:
        pass
    
    @abstractmethod
    def get_all_between_dates(self, start_date: datetime, end_date: datetime) -> list[GamelogEntity]:
        pass

    @abstractmethod
    def get_all(self) -> list[GamelogEntity]:
        pass

    @abstractmethod
    def get_all_by_player_id_and_season(self, player_id: str, season: int) -> list[GamelogEntity]:
        pass
