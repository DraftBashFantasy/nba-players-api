from interfaces.repositories import ITeamRepository
from domain.entities import TeamEntity
from interfaces.external import ITeamsFetcherService


class UpsertTeamsUseCase:
    """
    This class is responsible for upserting teams into the database.
    
    :param team_repository ITeamRepository: The repository for teams.
    :param teams_fetcher ITeamsFetcherService: The service for fetching teams.
    """

    def __init__(self, team_repository: ITeamRepository, teams_fetcher: ITeamsFetcherService):
        self._team_repository = team_repository
        self._teams_fetcher = teams_fetcher

    def execute(self) -> None:
        """
        This method is responsible for upserting the week's scheduled matchups into the database.
        
        :param teams: list[Team]
        """
        
        teams: list[TeamEntity] = self._teams_fetcher.execute()
        self._team_repository.upsert_many(teams)
