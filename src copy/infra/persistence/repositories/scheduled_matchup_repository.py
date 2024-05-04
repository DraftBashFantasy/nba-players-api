from datetime import datetime, timezone

from pymongo import UpdateOne
from interfaces.repositories import IScheduledMatchupRepository
from infra.persistence.database import scheduled_matchups_collection
from domain.entities import ScheduledMatchupEntity


class ScheduledMatchupRepository(IScheduledMatchupRepository):
    """
    Repository for scheduled matchups.
    """

    def __init__(self):
        self._scheduled_matchups_collection = scheduled_matchups_collection

    def upsert_many(self, scheduled_matchups: list[ScheduledMatchupEntity]) -> None:
        """
        Upsert a scheduled matchup.
        """

        bulk_operations = []

        for matchup in scheduled_matchups:
            bulk_operations.append(
                UpdateOne(
                    {"gameId": matchup.gameId},
                    {"$set": dict(matchup)},
                    upsert=True
                )
            )

        self._scheduled_matchups_collection.bulk_write(bulk_operations)

    def get_scheduled_matchups(self) -> list[ScheduledMatchupEntity]:
        """
        Gets all scheduled matchups from the database.
        
        :return: list of all scheduled matchups for the current season.add()
        :rtype: list[ScheduledMatchupEntity]
        """

        # Find all scheduled matchups from the database.
        scheduled_matchups = []
        for scheduled_matchup in self._scheduled_matchups_collection.find():
            # ** is used to unpack the dictionary into keyword arguments to create the entity.
            scheduled_matchups.append(ScheduledMatchupEntity(**scheduled_matchup))
        return scheduled_matchups

    def get_matchups_between_dates(self, start_date: datetime, end_date: datetime) -> list[ScheduledMatchupEntity]:
        """
        Gets a list of scheduled matchups within a date range.

        :param start_date datetime: The start date for the range of matchups.
        :param end_date datetime: The end date for the range of matchups.
        :returns: list of scheduled matchups within the date range.
        :rtype: list[ScheduledMatchupEntity]
        """

        # Convert start_date and end_date to UTC time if they are not already in UTC
        if start_date.tzinfo is None or start_date.tzinfo.utcoffset(start_date) is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None or end_date.tzinfo.utcoffset(end_date) is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        # Format the start_date and end_date to match the format in the database, ISO 8601 format with UTC timezone
        formatted_start_date = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        formatted_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Find all scheduled matchups within the date range from the database.
        scheduled_matchups = []
        for scheduled_matchup in self._scheduled_matchups_collection.find(
            {"dateTimeUTC": {"$gte": formatted_start_date, "$lte": formatted_end_date}}
        ):

            # ** is used to unpack the dictionary into keyword arguments to create the entity.
            scheduled_matchups.append(ScheduledMatchupEntity(**scheduled_matchup))
        return scheduled_matchups
