import asyncio
from typing import Optional
from fastapi import APIRouter, Query, Response, Path
import requests
from src.domain.entities.team_entity import TeamEntity
from src.infra.external.players_season_projections_fetcher import PlayersSeasonProjectionsFetcher
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
from nba_api.stats.static import teams as teams_fetcher, players as nba_api_players_fetcher
from src.infra.external.testing import Testing

players_router = APIRouter()

# Dependencies for dependency injection
player_repository = PlayerRepository()
team_repository = TeamRepository()
players_fetcher = PlayersFetcher()
projection_repository = PlayerRepository()
gamelog_repository = GamelogRepository()
scheduled_matchup_repository = ScheduledMatchupRepository()
gamelogs_repository = GamelogRepository()
gamelogs_fetcher = GamelogsFetcher()
player_weekly_projections_forecaster_service = PlayerWeeklyProjectionsForecasterService()


@players_router.get("/api/v1/testing1")
async def testing():
    try:
        return Testing().execute()
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing3")
async def testing():
    try:
        sleeper_api_players: dict = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        player_name_to_sleeper_api_id_dict: dict = {
            player_data.get("full_name", player_id): player_id
            for player_id, player_data in sleeper_api_players.items()
            if player_data.get("status") == "ACT"
        }
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: dict[str, dict] = season_projections_fetcher.fetch_projections()

        return {
            "player_name_to_sleeper_api_id_dict": player_name_to_sleeper_api_id_dict,
            "players_season_projections": players_season_projections,
        }
    except Exception as e:
        return Response(status_code=500, content=str(e))

@players_router.get("/api/v1/testing4")
async def testing():
    try:
        sleeper_api_players: dict = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        player_name_to_sleeper_api_id_dict: dict = {
            player_data.get("full_name", player_id): player_id
            for player_id, player_data in sleeper_api_players.items()
            if player_data.get("status") == "ACT"
        }
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: dict[str, dict] = season_projections_fetcher.fetch_projections()

        ADDS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        await asyncio.sleep(2)
        player_adds_dict: dict = {record["player_id"]: record["count"] for record in requests.get(ADDS_URL).json()}

        # Get the players that are currently being dropped the most in Sleeper's fantasy app
        DROPS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/drop?limit=50"
        asyncio.sleep(2)
        player_drops_dict: dict = {record["player_id"]: record["count"] for record in requests.get(DROPS_URL).json()}

        return {
            "player_drop_dict": player_drops_dict,
            "player_add_dict": player_adds_dict,
            "player_name_to_sleeper_api_id_dict": player_name_to_sleeper_api_id_dict,
            "players_season_projections": players_season_projections,
        }

    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing2")
async def testing():
    try:
        teams_dict: dict = {}
        for team in teams_fetcher.get_teams():
            teams_dict[team["abbreviation"]] = TeamEntity(
                teamId=str(team["id"]), location=team["city"], name=team["nickname"], abbreviation=team["abbreviation"]
            )
        nba_api_players: list[dict] = nba_api_players_fetcher.get_players()
        sleeper_api_players: dict = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        player_name_to_sleeper_api_id_dict: dict = {
            player_data.get("full_name", player_id): player_id
            for player_id, player_data in sleeper_api_players.items()
            if player_data.get("status") == "ACT"
        }
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: dict[str, dict] = season_projections_fetcher.fetch_projections()
        ADDS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_adds_dict: dict = {record["player_id"]: record["count"] for record in requests.get(ADDS_URL).json()}

        # Get the players that are currently being dropped the most in Sleeper's fantasy app
        DROPS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/drop?limit=50"
        player_drops_dict: dict = {record["player_id"]: record["count"] for record in requests.get(DROPS_URL).json()}
        
        return {
            "teams_dict": teams_dict,
            "nba_api_players": nba_api_players,
            "sleeper_api_players": sleeper_api_players,
            "player_name_to_sleeper_api_id_dict": player_name_to_sleeper_api_id_dict,
            "players_season_projections": players_season_projections,
            "player_adds_dict": player_adds_dict,
            "player_drops_dict": player_drops_dict
        }
        
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing/teams")
async def testing():
    try:
        teams_dict: dict = {}
        for team in teams_fetcher.get_teams():
            teams_dict[team["abbreviation"]] = TeamEntity(
                teamId=str(team["id"]), location=team["city"], name=team["nickname"], abbreviation=team["abbreviation"]
            )
        return teams_dict
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing/players")
async def testing():
    try:
        nba_api_players: list[dict] = nba_api_players_fetcher.get_players()
        return nba_api_players
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing/sleeper")
async def testing():
    try:
        # Get the NBA players from the Sleeper API
        sleeper_api_players: dict = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        player_name_to_sleeper_api_id_dict: dict = {
            player_data.get("full_name", player_id): player_id
            for player_id, player_data in sleeper_api_players.items()
            if player_data.get("status") == "ACT"
        }
        return player_name_to_sleeper_api_id_dict
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing/projections")
async def testing():
    try:
        # Get the player's projected season stats and rankings for points and category leagues
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: dict[str, dict] = season_projections_fetcher.fetch_projections()
        return players_season_projections
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.get("/api/v1/testing/adds")
async def testing():
    try:
        # Get the players that are currently being added the most in Sleeper's fantasy app
        ADDS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_adds_dict: dict = {record["player_id"]: record["count"] for record in requests.get(ADDS_URL).json()}

        # Get the players that are currently being dropped the most in Sleeper's fantasy app
        DROPS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/drop?limit=50"
        player_drops_dict: dict = {record["player_id"]: record["count"] for record in requests.get(DROPS_URL).json()}

        return {"drops": player_drops_dict, "adds": player_adds_dict}
    except Exception as e:
        return Response(status_code=500, content=str(e))


@players_router.post("/api/v1/players")
async def upsert_players():
    try:
        await PlayersUpserterUseCase(player_repository, players_fetcher).execute()
        return Response(status_code=200)
    except Exception as e:
        return Response(status_code=500, content=str(e))


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


@players_router.get("/api/v1/players/{player_id}/gamelogs")
async def get_gamelogs(
    player_id: str = Path(..., title="The player ID"), season: int = Query(None, title="The season")
):
    return [dict(gamelog) for gamelog in gamelogs_repository.get_all_by_player_id_and_season(player_id, season)]


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
