from datetime import datetime
from pymongo import UpdateOne
from src.interfaces.repositories import IProjectionRepository
from src.infra.persistence.database import projections_collection
from src.domain.entities import ProjectionEntity


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
        current_date_utc = datetime.utcnow()  # Get the current date in UTC

        bulk_operations = []
        for projection in projections:
            # Check if projection's dateUTC is beyond the current date
            if projection.dateUTC > current_date_utc:
                bulk_operations.append(UpdateOne({"gameId": projection.gameId}, {"$set": dict(projection)}, upsert=True))

        self._projections_collection.bulk_write(bulk_operations)
