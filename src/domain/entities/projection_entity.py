from pydantic import BaseModel
from src.domain.entities.team_entity import TeamEntity


class ProjectionEntity(BaseModel):
    gameId: str
    dateUTC: str
    playerId: str
    playerTeam: TeamEntity
    opposingTeam: TeamEntity
    fieldGoalsAttempted: float
    fieldGoalsMade: float
    threesMade: float
    points: float
    steals: float
    blocks: float
    assists: float
    rebounds: float
    turnovers: float
    freeThrowsAttempted: float
    freeThrowsMade: float

    def __iter__(self):  # type: ignore
        iter_dict = {
            "gameId": self.gameId,
            "playerId": self.playerId,
            "dateUTC": self.dateUTC,
            "playerTeam": dict(self.playerTeam),
            "opposingTeam": dict(self.opposingTeam),
            "fieldGoalsAttempted": self.fieldGoalsAttempted,
            "fieldGoalsMade": self.fieldGoalsMade,
            "threesMade": self.threesMade,
            "points": self.points,
            "steals": self.steals,
            "blocks": self.blocks,
            "assists": self.assists,
            "rebounds": self.rebounds,
            "turnovers": self.turnovers,
            "freeThrowsAttempted": self.freeThrowsAttempted,
            "freeThrowsMade": self.freeThrowsMade,
        }
        return iter(iter_dict.items())
