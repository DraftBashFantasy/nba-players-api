from fastapi import APIRouter, Response, Query
from src.infra.persistence.repositories import ScheduledMatchupRepository
from src.app.use_cases.scheduled_matchups.queries.get_scheduled_matchups_use_case import GetScheduledMatchupsUseCase
from src.domain.entities.scheduled_matchup_entity import ScheduledMatchupEntity
from src.infra.external import ScheduledMatchupsFetcherService
from src.app.use_cases.scheduled_matchups import ScheduledMatchupsUpserterUseCase

scheduled_matchups_router = APIRouter()
scheduled_matchup_repository = ScheduledMatchupRepository()
weekly_matchups_fetcher = ScheduledMatchupsFetcherService()


@scheduled_matchups_router.get("/api/v1/matchups/schedules")
async def get_scheduled_matchups(is_current_week: str = Query(None)):
    get_scheduled_matchups_use_case = GetScheduledMatchupsUseCase(scheduled_matchup_repository)
    scheduled_matchups = []
    if bool(is_current_week):
        scheduled_matchups: list[ScheduledMatchupEntity] = get_scheduled_matchups_use_case.get_current_week()
    else:
        scheduled_matchups: list[ScheduledMatchupEntity] = get_scheduled_matchups_use_case.get_all()
    return [dict(scheduled_matchup) for scheduled_matchup in scheduled_matchups]


@scheduled_matchups_router.post("/api/v1/matchups/schedules")
async def upsert_scheduled_matchups():
    try:
        scheduled_matchups_upserter_use_case = ScheduledMatchupsUpserterUseCase(scheduled_matchup_repository, weekly_matchups_fetcher)
        scheduled_matchups_upserter_use_case.execute()
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500, content=str(e))
