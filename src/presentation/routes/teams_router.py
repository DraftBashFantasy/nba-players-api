from fastapi import APIRouter, Response
from infra.persistence.repositories import TeamRepository
from infra.external import TeamsFetcher
from app.use_cases.teams.commands.upsert_teams_use_case import UpsertTeamsUseCase

teams_router = APIRouter()

teams_repository = TeamRepository()
teams_fetcher = TeamsFetcher()


@teams_router.post("/api/v1/teams")
async def upsert_scheduled_matchups():
    use_case = UpsertTeamsUseCase(teams_repository, teams_fetcher)
    use_case.execute()
    return Response(status_code=200)
