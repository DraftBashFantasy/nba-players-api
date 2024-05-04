import nba_api.stats
import requests
from datetime import datetime
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster
from src.domain.entities import PlayerEntity, TeamEntity
from src.infra.external import PlayersSeasonProjectionsFetcher
from src.interfaces.repositories import ITeamRepository
from src.domain.value_objects import PlayerSeasonProjections, PlayerSeasonTotals
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

        nba_api_players: list[dict] = []
        for team in teams.get_teams():
            for nba_api_player in commonteamroster.CommonTeamRoster(team_id=team["id"]).get_dict()["resultSets"][0]["rowSet"]:
                nba_api_players.append(
                    {
                        "playerId": nba_api_player[-2],
                        "firstName": nba_api_player[3].split(" ")[0],
                        "lastName": nba_api_player[3].split(" ")[1],
                        "team": {
                            "teamId": str(team["id"]),
                            "name": team["nickname"],
                            "abbreviation": team["abbreviation"],
                            "location": team["city"]
                        }
                    }
                )

        # Get the NBA players from the Sleeper API
        sleeper_api_players: list[dict] = requests.get(url="https://api.sleeper.app/v1/players/nba")

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
                first_name: str = nba_api_player["firstName"]
                last_name: str = nba_api_player["lastName"]
                team: TeamEntity = TeamEntity(**nba_api_player["team"])
                season_projections = None

                # Get the player's information from Sleeper's API
                for sleeper_player_id, sleeper_player in sleeper_api_players.json().items():
                    if (
                        first_name == sleeper_player["first_name"]
                        and last_name == sleeper_player["last_name"]
                        and dict(team)["abbreviation"] == sleeper_player["team"]
                    ):
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
                        sleeper_api_player = sleeper_player
                        break

                # If their is not a corresponding player in the Sleeper API, skip this player.
                if sleeper_api_player is None:
                    continue

                # Get the player's rankings for points and category leagues
                for projections in players_season_projections:
                    if (
                        first_name == projections["firstName"]
                        and last_name == projections["lastName"]
                        and dict(team)["abbreviation"] == projections["teamAbbreviation"]
                    ):
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
                    playerId=str(nba_api_player["playerId"]),
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
