from abc import ABC, abstractmethod
from domain.entities import ScheduledMatchupEntity


class ITeamsFetcherService(ABC):
    """
    Interface for scheduled matchups fetcher service
    """

    @abstractmethod
    def execute(self) -> list[ScheduledMatchupEntity]:
        pass
