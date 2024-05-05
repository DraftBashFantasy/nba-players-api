from datetime import datetime
from src.domain.value_objects import PlayerSeasonTotals
from src.infra.persistence.database import players_collection, gamelogs_collection
from src.domain.entities import PlayerEntity, ProjectionEntity
from src.interfaces.repositories import IPlayerRepository
from pymongo import UpdateOne


class PlayerRepository(IPlayerRepository):
    """
    Repository for NBA players.
    """

    def __init__(self) -> None:
        self._players_collection = players_collection

    def get_all(self) -> list[PlayerEntity]:
        """
        Get all NBA players from the database.

        :return: A list of all NBA players in the database.
        :rtype: list[PlayerEntity]
        """

        return [PlayerEntity(**player) for player in self._players_collection.find()]

    def upsert_many_projections(self, projections: list[ProjectionEntity]) -> None:
        """
        Upsert the projections for multiple players in bulk.

        :param projections: A list of projection entities to upsert.
        """
        # Initialize a list to store bulk update operations
        bulk_operations = []

        # Iterate through each projection entity
        for projection in projections:
            # Create an UpdateOne operation for each projection entity
            bulk_operations.append(
                UpdateOne(
                    # Specify the filter to identify the player document
                    {"playerId": projection.playerId},
                    # Specify the update operation using MongoDB aggregation pipeline syntax
                    [
                        {
                            "$set": {
                                "currentWeekProjections": {
                                    "$cond": {
                                        # Condition: Check if the projection's gameId exists in currentWeekProjections
                                        "if": {"$in": [projection.gameId, "$currentWeekProjections.gameId"]},
                                        # If gameId exists, update the matching projection
                                        "then": {
                                            "$map": {
                                                "input": "$currentWeekProjections",
                                                "as": "proj",
                                                "in": {
                                                    "$cond": {
                                                        "if": {"$eq": ["$$proj.gameId", projection.gameId]},
                                                        "then": dict(projection),
                                                        "else": "$$proj",
                                                    }
                                                },
                                            }
                                        },
                                        # If gameId doesn't exist, append the new projection to currentWeekProjections
                                        "else": {"$concatArrays": ["$currentWeekProjections", [dict(projection)]]},
                                    }
                                }
                            }
                        }
                    ],
                    # Set upsert=True to insert a new document if no match is found
                    upsert=True,
                )
            )

        # Execute bulk write operations
        self._players_collection.bulk_write(bulk_operations)

    def upsert_many(self, players: list[PlayerEntity]) -> None:
        """
        Bulk upsert NBA players.

        :param players: A list of player entities to upsert.
        """
        bulk_operations = []

        # Collect all player IDs from the list of player entities
        player_ids = [player.playerId for player in players]

        # Retrieve existing documents for the provided player IDs
        existing_players = self._players_collection.find({"playerId": {"$in": player_ids}})
        existing_player_ids = set(player["playerId"] for player in existing_players)

        for player in players:
            # For insertions, include all fields
            player_document = dict(player)

            # For updates, exclude specified fields
            if player.playerId in existing_player_ids:
                exclude_fields = ["currentWeekProjections", "recentNews", "fantasyOutlook"]
                for field in exclude_fields:
                    player_document.pop(field, None)

            # Create an UpdateOne operation for each player entity
            bulk_operations.append(UpdateOne({"playerId": player.playerId}, {"$set": player_document}, upsert=True))

        # Execute bulk write operations
        self._players_collection.bulk_write(bulk_operations)

    def get_season_totals(self, season: int) -> dict[str, PlayerSeasonTotals]:
        """
        Get the season totals for all players in the database.
        
        :param season int: The season for which to retrieve player totals.
        :return: A dictionary mapping player IDs to their season totals.
        :rtype: dict[str, PlayerSeasonTotals]
        """

        players_totals: list[PlayerSeasonTotals] = gamelogs_collection.aggregate(
            [
                {"$match": {"season": season}},
                {"$match": {"isActive": True}},
                {
                    "$group": {
                        "_id": "$playerId",
                        "points": {"$sum": "$points"},
                        "reboundsTotal": {"$sum": "$reboundsTotal"},
                        "assists": {"$sum": "$assists"},
                        "steals": {"$sum": "$steals"},
                        "blocks": {"$sum": "$blocks"},
                        "turnovers": {"$sum": "$turnovers"},
                        "fieldGoalsAttempted": {"$sum": "$fieldGoalsAttempted"},
                        "fieldGoalsMade": {"$sum": "$fieldGoalsMade"},
                        "threesMade": {"$sum": "$threesMade"},
                        "freeThrowsAttempted": {"$sum": "$freeThrowsAttempted"},
                        "freeThrowsMade": {"$sum": "$freeThrowsMade"},
                        "minutes": {"$sum": "$minutes"},
                        "gamesPlayed": {"$sum": 1},
                    }
                },
            ]
        )
        
        return {player_totals.pop("_id"): player_totals for player_totals in players_totals}
