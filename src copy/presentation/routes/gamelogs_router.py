from typing import Optional
from fastapi import APIRouter, Query, Response
from infra.external import GamelogsFetcher
from infra.persistence.repositories import GamelogRepository
from app.use_cases.gamelogs import GamelogsUpserterUseCase

gamelogs_router = APIRouter()
gamelogs_repository = GamelogRepository()
gamelogs_fetcher = GamelogsFetcher()


@gamelogs_router.post("/api/v1/gamelogs")
async def upsert_gamelogs(season: Optional[int] = Query(None)):
    GamelogsUpserterUseCase(gamelogs_repository, gamelogs_fetcher).execute(season)
    return Response(status_code=200)


@gamelogs_router.get("/api/v1/gamelogs")
async def get_gamelogs():
    return [dict(gamelog) for gamelog in gamelogs_repository.get_all()]
