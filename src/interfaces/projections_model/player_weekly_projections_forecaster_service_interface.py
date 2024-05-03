from abc import ABC, abstractmethod
from domain.entities import ProjectionEntity, GamelogEntity, ScheduledMatchupEntity, PlayerEntity


class IPlayerWeeklyProjectionsForecasterService(ABC):
    """
    Interface for gamelogs fetcher
    """

    @abstractmethod
    def execute(
        self,
        gamelogs: list[GamelogEntity],
        scheduled_matchups: list[ScheduledMatchupEntity],
        players: list[PlayerEntity],
    ) -> list[ProjectionEntity]:
        pass
