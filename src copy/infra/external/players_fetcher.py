import requests
from datetime import datetime
from domain.entities import PlayerEntity
from infra.external import PlayersSeasonProjectionsFetcher
from interfaces.repositories import ITeamRepository
from domain.value_objects import PlayerSeasonProjections, PlayerSeasonTotals
from interfaces.external import IPlayersFetcher


class PlayersFetcher(IPlayersFetcher):
    """
    Fetches NBA players and their relevant data from APIs.

    This class integrates multiple APIs and web scrapers to gather NBA player data,
    including projections, rankings, and other relevant information.

    :param team_repository ITeamRepository: An instance of a team repository implementing the
        ITeamRepository interface, used to interact with the team data in the database.
    """

    def __init__(self, team_repository: ITeamRepository):
        self.team_repository = team_repository

        # These headers are needed to access the NBA API
        self._nba_api_headers = {
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "x-nba-stats-token": "true",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "x-nba-stats-origin": "stats",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Referer": "https://stats.nba.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def fetch_new_player_data(self) -> list[PlayerEntity]:
        """ Fetches NBA players from APIs.

        :return: A list of player entities
        :rtype: list[PlayerEntity]
        """

        # Get the current NBA season, i.e. 2023-24
        current_season = datetime.now().year
        if datetime.now().month < 10:
            season = f"{int(current_season) - 1}-{str(current_season)[2:]}"
        elif datetime.now().month >= 10:
            season = f"{current_season}-{str(int(current_season) + 1)[2:]}"

        # Get the NBA players from the NBA API
        nba_api_players = []
        try:
            NBA_PLAYERS_API = (
                "https://stats.nba.com/stats/leaguedashplayerstats?LastNGames=0&LeagueID=00"
                + "&MeasureType=Base&Month=0&OpponentTeamID=0&PORound=0&PerMode=Totals&Period=0"
                + f"&PlusMinus=N&Season={season}&SeasonType=Regular+Season&StarterBench=&TeamID=0"
            )
            nba_players_response = requests.get(url=NBA_PLAYERS_API, headers=self._nba_api_headers)
            nba_api_players = nba_players_response.json()["resultSets"][0]["rowSet"]
        except Exception as e:
            raise Exception(f"Error fetching NBA players from NBA API: {e}")

        # Get the NBA players from the Sleeper API
        SLEEPER_PLAYERS_API = "https://api.sleeper.app/v1/players/nba"
        sleeper_api_players = requests.get(url=SLEEPER_PLAYERS_API)

        # Get the player's projected season stats and rankings for points and category leagues
        season_projections_fetcher = PlayersSeasonProjectionsFetcher()
        players_season_projections = season_projections_fetcher.fetch_projections()

        # Get the players that are currently being added the most in Sleeper's fantasy app
        ADDS_URL = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_drops_list = requests.get(ADDS_URL).json()

        # Get the players that are currently being dropped the most in Sleeper's fantasy app
        DROPS_URL = "https://api.sleeper.app/v1/players/nba/trending/add?limit=50"
        player_adds_list = requests.get(DROPS_URL).json()

        # Create a list of player entities
        players_list = []
        for nba_api_player in nba_api_players:
            try:
                sleeper_api_player = None
                drop_count = None  # Number of times the player has been dropped in sleeper during the last 24 hours.
                add_count = None  # Number of times the player has been added in sleeper during the last 24 hours.
                first_name = nba_api_player[1].split(" ")[0]
                last_name = nba_api_player[1].split(" ")[1]
                team_id = str(nba_api_player[3])
                team = self.team_repository.get_team(team_id)  # Team with name, id, etc
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

                season_totals = PlayerSeasonTotals(
                    gamesPlayed=int(nba_api_player[6]),
                    minutes=float(nba_api_player[10]),
                    fieldGoalsMade=int(nba_api_player[11]),
                    fieldGoalsAttempted=int(nba_api_player[12]),
                    threesMade=int(nba_api_player[14]),
                    points=int(nba_api_player[30]),
                    steals=int(nba_api_player[25]),
                    blocks=int(nba_api_player[26]),
                    assists=int(nba_api_player[23]),
                    rebounds=int(nba_api_player[22]),
                    turnovers=int(nba_api_player[24]),
                    freeThrowsAttempted=int(nba_api_player[17]),
                    freeThrowsMade=int(nba_api_player[18]),
                )

                # Combine all the player's information into a PlayerEntity object.
                player_entity = PlayerEntity(
                    playerId=str(nba_api_player[0]),
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
                    seasonTotals=season_totals,
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
