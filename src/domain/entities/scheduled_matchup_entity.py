from pydantic import BaseModel
from src.domain.entities.team_entity import TeamEntity

class ScheduledMatchupEntity(BaseModel):
    gameId: str
    dateTimeUTC: str
    homeTeam: TeamEntity
    awayTeam: TeamEntity
    
    def __iter__(self): # type: ignore
        iter_dict = {
            "gameId": self.gameId,
            "dateTimeUTC": self.dateTimeUTC,
            "homeTeam": dict(self.homeTeam),
            "awayTeam": dict(self.awayTeam),
        }
        return iter(iter_dict.items())
