from pydantic import BaseModel
from src.domain.entities.team_entity import TeamEntity

class GamelogEntity(BaseModel):
    gameId: str
    season: int
    dateUTC: str
    playerId: str
    playerTeam: TeamEntity
    isHomeGame: bool
    isActive: bool
    opposingTeam: TeamEntity
    playerTeamScore: int
    opposingTeamScore: int
    position: str
    isStarter: bool
    minutes: float
    points: int
    fieldGoalsMade: int
    fieldGoalsAttempted: int
    threesMade: int
    threesAttempted: int
    freeThrowsMade: int
    freeThrowsAttempted: int
    reboundsOffensive: int
    reboundsDefensive: int
    reboundsTotal: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    plusMinus: int

    def __iter__(self): # type: ignore
        iter_dict = {
            "gameId": self.gameId,
            "season": self.season,
            "dateUTC": self.dateUTC,
            "playerId": self.playerId,
            "playerTeam": dict(self.playerTeam),
            "isActive": self.isActive,
            "isHomeGame": self.isHomeGame,
            "opposingTeam": dict(self.opposingTeam),
            "playerTeamScore": self.playerTeamScore,
            "opposingTeamScore": self.opposingTeamScore,
            "position": self.position,
            "isStarter": self.isStarter,
            "minutes": self.minutes,
            "points": self.points,
            "fieldGoalsMade": self.fieldGoalsMade,
            "fieldGoalsAttempted": self.fieldGoalsAttempted,
            "threesMade": self.threesMade,
            "threesAttempted": self.threesAttempted,
            "freeThrowsMade": self.freeThrowsMade,
            "freeThrowsAttempted": self.freeThrowsAttempted,
            "reboundsOffensive": self.reboundsOffensive,
            "reboundsDefensive": self.reboundsDefensive,
            "reboundsTotal": self.reboundsTotal,
            "assists": self.assists,
            "steals": self.steals,
            "blocks": self.blocks,
            "turnovers": self.turnovers,
            "fouls": self.fouls,
            "plusMinus": self.plusMinus
        }
        return iter(iter_dict.items())