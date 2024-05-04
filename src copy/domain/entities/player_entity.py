from pydantic import BaseModel
from typing import Optional, List
from domain.entities.team_entity import TeamEntity
from domain.entities.projection_entity import ProjectionEntity
from domain.value_objects import PlayerSeasonTotals, PlayerSeasonProjections


class PlayerEntity(BaseModel):
    playerId: str
    rotowireId: Optional[str]
    firstName: str
    lastName: str
    fantasyPositions: List[str]
    position: str
    team: Optional[TeamEntity]
    height: int
    weight: int
    age: int
    currentWeekProjections: list[ProjectionEntity]
    depthChartOrder: Optional[int]
    injuryStatus: Optional[str]
    recentNews: Optional[str]
    fantasyOutlook: Optional[str]
    jerseyNumber: Optional[int]
    seasonProjections: Optional[PlayerSeasonProjections]
    seasonTotals: Optional[PlayerSeasonTotals]
    dropCount: Optional[int]
    addCount: Optional[int]

    def __iter__(self):  # type: ignore
        iter_dict = {
            "playerId": self.playerId,
            "rotowireId": self.rotowireId,
            "firstName": self.firstName,
            "lastName": self.lastName,
            "fantasyPositions": self.fantasyPositions,
            "position": self.position,
            "team": dict(self.team) if self.team else None,
            "height": self.height,
            "weight": self.weight,
            "age": self.age,
            "currentWeekProjections": [
                dict(current_week_projection) for current_week_projection in self.currentWeekProjections
            ],
            "depthChartOrder": self.depthChartOrder,
            "injuryStatus": self.injuryStatus,
            "recentNews": self.recentNews,
            "fantasyOutlook": self.fantasyOutlook,
            "jerseyNumber": self.jerseyNumber,
            "seasonProjections": dict(self.seasonProjections) if self.seasonProjections else None,
            "seasonTotals": dict(self.seasonTotals) if self.seasonTotals else None,
            "dropCount": self.dropCount,
            "addCount": self.addCount,
        }
        return iter(iter_dict.items())
