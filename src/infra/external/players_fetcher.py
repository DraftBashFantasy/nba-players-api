import requests
from nba_api.stats.static import teams as teams_fetcher, players as nba_api_players_fetcher
from src.domain.entities import PlayerEntity, TeamEntity
from src.infra.external import PlayersSeasonProjectionsFetcher
from src.domain.value_objects import PlayerSeasonProjections
from src.interfaces.external import IPlayersFetcher


class PlayersFetcher(IPlayersFetcher):
    """
    Fetches NBA players and their relevant data from APIs.

    This class integrates multiple APIs and web scrapers to gather NBA player data,
    including projections, rankings, and other relevant information.
    """

    def execute(self) -> list[PlayerEntity]:
        """Fetches NBA players from APIs.

        :return: A list of player entities
        :rtype: list[PlayerEntity]
        """

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

        # Create a list of player entities
        players_list: list[PlayerEntity] = []
        for nba_api_player in nba_api_players:
            try:
                drop_count = None  # Number of times the player has been dropped in sleeper during the last 24 hours.
                add_count = None  # Number of times the player has been added in sleeper during the last 24 hours.
                first_name: str = nba_api_player["first_name"]
                last_name: str = nba_api_player["last_name"]
                full_name: str = f"{first_name} {last_name}"
                team: TeamEntity = None
                sleeper_id: str = player_name_to_sleeper_api_id_dict.get(full_name, None)
                sleeper_api_player = sleeper_api_players.get(sleeper_id)

                if sleeper_api_player is not None:
                    team = teams_dict.get(sleeper_api_player.get("team"))
                else:
                    continue

                # Get the player's add and drop counts from the Sleeper API
                add_count = player_adds_dict.get(sleeper_id)
                drop_count = player_drops_dict.get(sleeper_id)

                # Get the player's season projections and category/points league rankings
                season_projections: PlayerSeasonProjections = players_season_projections.get(full_name)

                # Combine all the player's information into a PlayerEntity object.
                player_entity = PlayerEntity(
                    playerId=str(nba_api_player["id"]),
                    rotowireId=str(sleeper_api_player["rotowire_id"]),  # Fantasy news provider.
                    firstName=first_name,
                    lastName=last_name,
                    fantasyPositions=sleeper_api_player["fantasy_positions"],
                    position=sleeper_api_player["position"],
                    team=team,
                    height=sleeper_api_player["height"],
                    weight=sleeper_api_player["weight"],
                    age=sleeper_api_player["age"],
                    currentWeekProjections=[],
                    jerseyNumber=sleeper_api_player["number"],
                    depthChartOrder=sleeper_api_player["depth_chart_order"],
                    injuryStatus=sleeper_api_player["injury_status"],
                    seasonProjections=season_projections,
                    seasonTotals=None,
                    addCount=add_count,
                    dropCount=drop_count,
                    recentNews=None,
                    fantasyOutlook=None,
                )

                players_list.append(player_entity)

            except Exception as e:
                print(f"Error creating player entity: {e.with_traceback()}")
                continue

        return players_list
