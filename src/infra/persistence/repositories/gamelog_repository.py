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
            for gamelog in self._gamelogs_collection.find({"playerId": player_id, "season": season})
        ]
