from typing import Optional
from pydantic import BaseModel

class PlayerSeasonProjections(BaseModel):
    
    pointsLeagueRanking: Optional[int]
    categoryLeagueRanking: Optional[int]
    gamesPlayed: int
    minutes: float
    fieldGoalPercentage: float
    threesMade: int
    points: int
    steals: int
    blocks: int
    assists: int
    rebounds: int
    turnovers: int
    freeThrowPercentage: float

    def dict(self) -> dict:
        return {
            'pointsLeagueRanking': self.pointsLeagueRanking,
            'categoriesLeagueRanking': self.categoriesLeagueRanking,
            'gamesPlayed': self.gamesPlayed,
            'minutes': self.minutes,
            'fieldGoalPercentage': self.fieldGoalPercentage,
            'threesMade': self.threesMade,
            'points': self.points,
            'steals': self.steals,
            'blocks': self.blocks,
            'assists': self.assists,
            'rebounds': self.rebounds,
            'turnovers': self.turnovers,
            'freeThrowPercentage': self.freeThrowPercentage
        }