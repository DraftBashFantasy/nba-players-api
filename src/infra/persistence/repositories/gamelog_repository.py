from datetime import datetime
from pymongo import UpdateOne
from src.infra.persistence.database import gamelogs_collection
from src.interfaces.repositories import IGamelogRepository
from src.domain.entities import GamelogEntity


class GamelogRepository(IGamelogRepository):
    """
    Repository for gamelogs.
    """

    def __init__(self):
        self._gamelogs_collection = gamelogs_collection

    def upsert_many(self, gamelogs: list[GamelogEntity]) -> None:
        """
        Upsert gamelogs in bulk.

        :param gamelogs list[GamelogEntity]: List of gamelog entities to upsert.
        """
        bulk_operations = []
        for gamelog in gamelogs:
            bulk_operations.append(
                UpdateOne(
                    {"playerId": gamelog.playerId, "gameId": gamelog.gameId}, {"$set": dict(gamelog)}, upsert=True
                )
            )
        self._gamelogs_collection.bulk_write(bulk_operations)

    def get_all_between_dates(self, start_date: datetime, end_date: datetime) -> list[GamelogEntity]:
        """
        Get gamelogs from the database within a specified date range.

        :param start_date: Start date of the range (inclusive).
        :param end_date: End date of the range (exclusive).
        :return: A list of gamelogs within the specified date range.
        """

        gamelogs: list[dict] = self._gamelogs_collection.find(
            {
                "dateUTC": {
                    "$gte": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "$lt": end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                },
                "isActive": True
            }
        )

        return [GamelogEntity(**gamelog) for gamelog in gamelogs]

    def get_all(self) -> list[GamelogEntity]:
        """
        Get all gamelogs from the database.

        :return list[GamelogEntity]: A list of all gamelogs in the database.
        """

        return [GamelogEntity(**gamelog) for gamelog in self._gamelogs_collection.find()]

    def get_all_by_player_id_and_season(self, player_id: str, season: int) -> list[GamelogEntity]:
        """
        Get all gamelogs of a given season from the database that belong to a certain player.

        :param player_id str: The ID of the player for which to retrieve gamelogs.
        :param season int: The season for which to retrieve gamelogs.
        :return list[GamelogEntity]: A list of gamelogs that match the criteria.
        """

        return [
            GamelogEntity(**gamelog)
            for gamelog in self._gamelogs_collection.find(
                {"playerId": player_id, "season": season, "isRegularSeasonGame": True}
            ).sort("dateUTC", -1)
        ]
