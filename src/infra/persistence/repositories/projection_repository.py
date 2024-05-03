from pymongo import UpdateOne
from interfaces.repositories import IProjectionRepository
from infra.persistence.database import projections_collection
from domain.entities import ProjectionEntity


class ProjectionRepository(IProjectionRepository):
    """
    Repository for player projections.
    """

    def __init__(self):
        self._projections_collection = projections_collection

    def upsert_many(self, projections: list[ProjectionEntity]) -> None:
        """
        Bulk upsert player projections.

        :param teams: A list of player game projections to upsert.
        """
        bulk_operations = []

        for projection in projections:
            bulk_operations.append(UpdateOne({"gameId": projection.gameId}, {"$set": dict(projection)}, upsert=True))

        self._projections_collection.bulk_write(bulk_operations)
