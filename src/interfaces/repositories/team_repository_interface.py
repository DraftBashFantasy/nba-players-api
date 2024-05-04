from abc import ABC, abstractmethod
from src.domain.entities import TeamEntity

class ITeamRepository(ABC):
    """ Interface for team repository. """

    @abstractmethod
    def upsert_many(self, teams: list[TeamEntity]) -> None:
        pass
    
    @abstractmethod
    def get_team(self, team_id: int) -> TeamEntity:
        pass