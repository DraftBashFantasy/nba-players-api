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
        sleeper_api_players: list[dict] = requests.get(url="https://api.sleeper.app/v1/players/nba").json()

        # Get the player's projected season stats and rankings for points and category leagues
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections: list[dict] = season_projections_fetcher.fetch_projections()

        # Get the players that are currently being added the most in Sleeper's fantasy app
        ADDS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_drops_list: list[dict] = requests.get(ADDS_URL).json()

        # Get the players that are currently being dropped the most in Sleeper's fantasy app
        DROPS_URL: str = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_adds_list: list[dict] = requests.get(DROPS_URL).json()

        # Create a list of player entities
        players_list: list[PlayerEntity] = []
        for nba_api_player in nba_api_players:
            try:
                sleeper_api_player = None
                drop_count = None  # Number of times the player has been dropped in sleeper during the last 24 hours.
                add_count = None  # Number of times the player has been added in sleeper during the last 24 hours.
                first_name: str = nba_api_player["first_name"]
                last_name: str = nba_api_player["last_name"]
                team: TeamEntity = None
                season_projections = None

                # Get the player's information from Sleeper's API
                for sleeper_player_id, sleeper_player in sleeper_api_players.items():
                    if first_name == sleeper_player["first_name"] and last_name == sleeper_player["last_name"]:
                        # Get the number of times the player has been added and dropped in Sleeper over the last 24 hours.
                        for player in player_drops_list:
                            if player["player_id"] == sleeper_player_id:
                                add_count = player["count"]
                                break
                        for player in player_adds_list:
                            if player["player_id"] == sleeper_player_id:
                                drop_count = player["count"]
                                break

                        # Returns player information from the sleeper API
                        team = teams_dict.get(sleeper_player["team"])
                        sleeper_api_player = sleeper_player
                        break

                # If their is not a corresponding player in the Sleeper API, skip this player.
                if sleeper_api_player is None:
                    continue

                # Get the player's rankings for points and category leagues
                for projections in players_season_projections:
                    if first_name == projections["firstName"] and last_name == projections["lastName"]:
                        
                        # Set the season projections for the player
                        season_projections = PlayerSeasonProjections(
                            pointsLeagueRanking=projections["pointsLeagueRanking"],
                            categoryLeagueRanking=projections["categoryLeagueRanking"],
                            points=projections["points"],
                            rebounds=projections["rebounds"],
                            assists=projections["assists"],
                            steals=projections["steals"],
                            blocks=projections["blocks"],
                            turnovers=projections["turnovers"],
                            fieldGoalPercentage=projections["fieldGoalPercentage"],
                            freeThrowPercentage=projections["freeThrowPercentage"],
                            threesMade=projections["threesMade"],
                            minutes=projections["minutes"],
                            gamesPlayed=projections["gamesPlayed"],
                        )
                        break

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
                print(f"Error creating player entity: {e}")
                continue

        return players_list
