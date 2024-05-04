from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities import ScheduledMatchupEntity

class IScheduledMatchupRepository(ABC):
    """
    Interface for scheduled matchup repository.
    """

    @abstractmethod
    def upsert_many(self, scheduled_matchups: list[ScheduledMatchupEntity]) -> None:
        """
        Upsert a scheduled matchup.
        """
        pass

    @abstractmethod 
    def get_scheduled_matchups(self) -> list[ScheduledMatchupEntity]:
        """
        Gets all scheduled matchups from the database.
        
        :return: list of all scheduled matchups for the current season.add()
        :rtype: list[ScheduledMatchupEntity]
        """
        pass

    @abstractmethod
    def get_matchups_between_dates(self, start_date: datetime, end_date: datetime) -> list[ScheduledMatchupEntity]:
        """
        Gets a list of scheduled matchups within a date range.

        :param start_date datetime: The start date for the range of matchups.
        :param end_date datetime: The end date for the range of matchups.
        :returns: list of scheduled matchups within the date range.
        :rtype: list[ScheduledMatchupEntity]
        """
        pass
