from pymongo import UpdateOne
from src.interfaces.repositories import ITeamRepository
from src.infra.persistence.database import teams_collection
from src.domain.entities import TeamEntity

class TeamRepository(ITeamRepository):
    """ 
    Repository for NBA teams. 
    """

    def __init__(self):
        self._teams_collection = teams_collection

    def upsert_many(self, teams: list[TeamEntity]) -> None:
        """
        Bulk upsert NBA teams.

        :param teams: A list of team entities to upsert.
        """
        bulk_operations = []

        for team in teams:
            bulk_operations.append(UpdateOne({"teamId": team.teamId}, {"$set": dict(team)}, upsert=True))

        self._teams_collection.bulk_write(bulk_operations)

    def get_team(self, team_id: int) -> TeamEntity:
        """ Get an NBA team
        :return: Team
        :param team_id: int
        """

        return TeamEntity(**self._teams_collection.find_one({"teamId": team_id}))
