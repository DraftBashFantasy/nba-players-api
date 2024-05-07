import requests
from nba_api.stats.static import teams as teams_fetcher, players as nba_api_players_fetcher
from src.domain.entities import PlayerEntity, TeamEntity
from src.infra.external import PlayersSeasonProjectionsFetcher
from src.domain.value_objects import PlayerSeasonProjections
from src.interfaces.external import IPlayersFetcher


class Testing:

    def execute(self) -> dict:

        teams_dict: dict = {}
        for team in teams_fetcher.get_teams():
            teams_dict[team["abbreviation"]] = TeamEntity(
                teamId=str(team["id"]), location=team["city"], name=team["nickname"], abbreviation=team["abbreviation"]
            )

        nba_api_players: list[dict] = nba_api_players_fetcher.get_players()

        # Get the NBA players from the Sleeper API
        sleeper_api_players: dict = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        player_name_to_sleeper_api_id_dict: dict = {
            player_data.get("full_name", player_id): player_id
            for player_id, player_data in sleeper_api_players.items()
            if player_data.get("status") == "ACT"
        }

        # Get the player's projected season stats and rankings for points and category leagues
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: dict[str, dict] = season_projections_fetcher.fetch_projections()

        # Get the players that are currently being added the most in Sleeper's fantasy app
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