from abc import ABC, abstractmethod
from src.domain.entities import ScheduledMatchupEntity


class IScheduledMatchupsFetcherService(ABC):
    """
    Interface for scheduled matchups fetcher service
    """

    @abstractmethod
    def execute(self) -> list[ScheduledMatchupEntity]:
        pass
