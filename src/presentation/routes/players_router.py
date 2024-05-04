from typing import Optional
from fastapi import APIRouter, Query, Response
from src.infra.persistence.repositories import (
    PlayerRepository,
    TeamRepository,
    GamelogRepository,
    ScheduledMatchupRepository,
)
from src.infra.external import PlayersFetcher, GamelogsFetcher
from src.infra.projections_model import PlayerWeeklyProjectionsForecasterService
from src.app.use_cases.players import PlayersUpserterUseCase
from src.app.use_cases.projections import PlayerWeeklyProjectionsForecasterUseCase
from src.app.use_cases.gamelogs import GamelogsUpserterUseCase

players_router = APIRouter()  # Router for players

# Dependencies for dependency injection
player_repository = PlayerRepository()
team_repository = TeamRepository()
players_fetcher = PlayersFetcher(team_repository)
projection_repository = PlayerRepository()
gamelog_repository = GamelogRepository()
scheduled_matchup_repository = ScheduledMatchupRepository()
gamelogs_repository = GamelogRepository()
gamelogs_fetcher = GamelogsFetcher()
player_weekly_projections_forecaster_service = PlayerWeeklyProjectionsForecasterService()


@players_router.post("/api/v1/players")
async def upsert_players():
    PlayersUpserterUseCase(player_repository, players_fetcher).execute()
    return Response(status_code=200)


@players_router.get("/api/v1/players")
async def get_players():
    return [dict(player) for player in player_repository.get_all()]


@players_router.post("/api/v1/players/gamelogs")
async def upsert_gamelogs(season: Optional[int] = Query(None)):
    GamelogsUpserterUseCase(gamelogs_repository, gamelogs_fetcher).execute(season)
    return Response(status_code=200)


@players_router.get("/api/v1/players/gamelogs")
async def get_gamelogs():
    return [dict(gamelog) for gamelog in gamelogs_repository.get_all()]


@players_router.post("/api/v1/players/projections")
async def upsert_players():
    PlayerWeeklyProjectionsForecasterUseCase(
        player_repository,
        gamelog_repository,
        scheduled_matchup_repository,
        projection_repository,
        player_weekly_projections_forecaster_service,
    ).execute()
    return Response(status_code=200)
