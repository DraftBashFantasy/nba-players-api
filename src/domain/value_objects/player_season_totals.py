from pydantic import BaseModel

class PlayerSeasonTotals(BaseModel):
    gamesPlayed: int
    minutes: float
    fieldGoalsAttempted: int
    fieldGoalsMade: int
    threesMade: int
    points: int
    steals: int
    blocks: int
    assists: int
    rebounds: int
    turnovers: int
    freeThrowsAttempted: int
    freeThrowsMade: int

    def dict(self) -> dict:
        return {
            'gamesPlayed': self.gamesPlayed,
            'minutes': self.minutes,
            'fieldGoalsAttempted': self.fieldGoalsAttempted,
            'fieldGoalsMade': self.fieldGoalsMade,
            'threesMade': self.threesMade,
            'points': self.points,
            'steals': self.steals,
            'blocks': self.blocks,
            'assists': self.assists,
            'rebounds': self.rebounds,
            'turnovers': self.turnovers,
            'freeThrowsAttempted': self.freeThrowsAttempted,
            'freeThrowsMade': self.freeThrowsMade
        }