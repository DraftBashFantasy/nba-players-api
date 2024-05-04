from pydantic import BaseModel

class TeamEntity(BaseModel):
    teamId: str
    abbreviation: str
    location: str
    name: str