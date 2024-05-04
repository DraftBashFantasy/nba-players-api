import time
import requests
from datetime import datetime, timedelta
from src.domain.entities import GamelogEntity, TeamEntity
from src.interfaces.external import IGamelogsFetcher


class GamelogsFetcher(IGamelogsFetcher):
    """
    Fetches NBA player gamelogs according to the given game_ids.

    :param get_recent_game_ids: Gets the game_ids over the last 10 days
    :param get_season_game_ids: Gets the game_ids for a given season.
    :param execute: Fetches NBA player gamelogs according to the given game_ids.
    """

    def get_recent_game_ids(self) -> list[int]:
        """
        Gets the game_ids over the last 3 days

        :return: A list of game_ids for the last 3 days.
        :rtype: list[int]
        """

        # Get the current date and the date 3 days ago
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        date_three_days_ago = (datetime.utcnow() - timedelta(days=3)).strftime("%Y-%m-%d")

        current_season = datetime.utcnow().year - 1
        if datetime.now().month >= 10:
            current_season = current_season

        recent_games = requests.get(
            "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/"
            + f"{current_season}/league/00_full_schedule.json"
        ).json()

        game_ids = []
        for recent_game in recent_games["lscd"]:
            games = recent_game["mscd"]["g"]
            for game in games:
                if game["gdte"] >= date_three_days_ago and game["gdte"] < current_date:
                    game_ids.append(game["gid"])

        return game_ids

    def get_season_game_ids(self, season: int) -> list[int]:
        """
        Gets the game_ids for a given season.

        :param season int: The season for which to get the game_ids, i.e. 2023 for the 2023-24 season.
        :return: A list of game_ids for the given season.
        :rtype: list[int]
        """

        # Get the game_ids for the given season
        recent_games = requests.get(
            "https://data.nba.com/data/10s/v2015/json/mobile_teams/nba/"
            + f"{season}/league/00_full_schedule.json"
        ).json()["lscd"]

        game_ids = []
        for recent_game in recent_games:
            games = recent_game["mscd"]["g"]
            for game in games:
                game_ids.append(game["gid"])
        return game_ids

    def get_new_gamelogs(self, game_ids: list[int]) -> list[GamelogEntity]:
        """
        Fetches NBA player gamelogs according to the given game_ids.

        :param game_ids list[int]: A list of game_ids for which to fetch gamelogs.
        :return: A list of gamelog entities for each given game_id
        :rtype: list[GamelogEntity]
        """

        # Gets player data, i.e. position, from Sleeper's API
        players_response = requests.get("https://api.sleeper.app/v1/players/nba")
        players_data = players_response.json()

        # Get the gamelogs for each player in each game
        gamelogs = []
        for game_id in game_ids:
            try:
                # Get the game data from the NBA API
                game_response = requests.get(
                    f"https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{game_id}.json"
                )
                game = game_response.json()["game"]

                # Get the date of the game
                game_date = game["gameTimeUTC"].split("T")[0]
                season = int(game_date.split("-")[0])
                month_number = int(game_date.split("-")[1])
                if month_number >= 1 and month_number < 10:
                    season -= 1

                # Get home team players and team id
                home_team = game["homeTeam"]
                home_team_id = home_team["teamId"]
                home_players = home_team["players"]

                # Get away team players and team id
                away_team = game["awayTeam"]
                away_team_id = away_team["teamId"]
                away_players = away_team["players"]

                # Get the gamelogs for the home players
                for home_player in home_players:
                    stats = home_player["statistics"]
                    position = "NaN"  # Position the player plays, i.e. power forward, shooting guard, etc
                    minutes = float(stats["minutes"].split("M")[0][2:])
                    seconds = float(stats["minutes"].split("M")[1][:2])
                    minutes_played = minutes + (seconds / 60)
                    is_active = int(home_player.get("notPlayingReason") is None)

                    # Get the player's position from the player data fetched from Sleeper's API
                    for key, player in players_data.items():
                        if (
                            player["first_name"] == home_player["firstName"]
                            and player["last_name"] in home_player["familyName"]
                        ):
                            position = player["position"]
                            break

                    gamelogs.append(
                        GamelogEntity(
                            gameId=str(game_id),
                            season=season,
                            dateUTC=game["gameTimeUTC"],
                            playerId=str(home_player["personId"]),
                            playerTeam=TeamEntity(
                                teamId=str(home_team_id),
                                abbreviation=home_team["teamTricode"],
                                location=home_team["teamCity"],
                                name=home_team["teamName"],
                            ),
                            isHomeGame=True,
                            opposingTeam=TeamEntity(
                                teamId=str(away_team_id),
                                abbreviation=away_team["teamTricode"],
                                location=away_team["teamCity"],
                                name=away_team["teamName"],
                            ),
                            isActive=is_active,
                            playerTeamScore=home_team["score"],
                            opposingTeamScore=away_team["score"],
                            position=position,
                            isStarter=home_player["starter"],
                            minutes=minutes_played,
                            points=stats["points"],
                            fieldGoalsMade=stats["fieldGoalsMade"],
                            threesMade=stats["threePointersMade"],
                            fieldGoalsAttempted=stats["fieldGoalsAttempted"],
                            threesAttempted=stats["threePointersAttempted"],
                            freeThrowsMade=stats["freeThrowsMade"],
                            freeThrowsAttempted=stats["freeThrowsAttempted"],
                            reboundsOffensive=stats["reboundsOffensive"],
                            reboundsDefensive=stats["reboundsDefensive"],
                            reboundsTotal=stats["reboundsTotal"],
                            assists=stats["assists"],
                            steals=stats["steals"],
                            blocks=stats["blocks"],
                            turnovers=stats["turnovers"],
                            fouls=stats["foulsPersonal"],
                            plusMinus=stats["plusMinusPoints"],
                        )
                    )

                # Get the gamelogs for the away players
                for away_player in away_players:
                    stats = away_player["statistics"]
                    position = "NaN"
                    minutes = float(stats["minutes"].split("M")[0][2:])
                    seconds = float(stats["minutes"].split("M")[1][:2])
                    minutes_played = minutes + (seconds / 60)
                    is_active = int(away_player.get("notPlayingReason") is None)

                    # Get the player's position from the player data fetched from Sleeper's API
                    for key, player in players_data.items():
                        if (
                            player["first_name"] == away_player["firstName"]
                            and player["last_name"] in away_player["familyName"]
                        ):
                            position = player[
                                "position"
                            ]  # Position the player plays, i.e. center, pointguard, smallforward, etc

                    gamelogs.append(
                        GamelogEntity(
                            gameId=str(game_id),
                            season=season,
                            dateUTC=game["gameTimeUTC"],
                            playerId=str(away_player["personId"]),
                            playerTeam=TeamEntity(
                                teamId=str(away_team_id),
                                abbreviation=away_team["teamTricode"],
                                location=away_team["teamCity"],
                                name=away_team["teamName"],
                            ),
                            isHomeGame=True,
                            opposingTeam=TeamEntity(
                                teamId=str(home_team_id),
                                abbreviation=home_team["teamTricode"],
                                location=home_team["teamCity"],
                                name=home_team["teamName"],
                            ),
                            isActive=is_active,
                            playerTeamScore=away_team["score"],
                            opposingTeamScore=home_team["score"],
                            position=position,
                            isStarter=away_player["starter"],
                            minutes=minutes_played,
                            points=stats["points"],
                            fieldGoalsMade=stats["fieldGoalsMade"],
                            threesMade=stats["threePointersMade"],
                            fieldGoalsAttempted=stats["fieldGoalsAttempted"],
                            threesAttempted=stats["threePointersAttempted"],
                            freeThrowsMade=stats["freeThrowsMade"],
                            freeThrowsAttempted=stats["freeThrowsAttempted"],
                            reboundsOffensive=stats["reboundsOffensive"],
                            reboundsDefensive=stats["reboundsDefensive"],
                            reboundsTotal=stats["reboundsTotal"],
                            assists=stats["assists"],
                            steals=stats["steals"],
                            blocks=stats["blocks"],
                            turnovers=stats["turnovers"],
                            fouls=stats["foulsPersonal"],
                            plusMinus=stats["plusMinusPoints"],
                        )
                    )
            except Exception as e:
                print(f"Error: {e}")
            finally:
                time.sleep(0.05)

        return gamelogs
