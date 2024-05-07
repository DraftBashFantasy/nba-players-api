import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.domain.entities import GamelogEntity, ScheduledMatchupEntity, PlayerEntity, TeamEntity, ProjectionEntity
from src.interfaces.projections_model import IPlayerWeeklyProjectionsForecasterService


class PlayerWeeklyProjectionsForecasterService(IPlayerWeeklyProjectionsForecasterService):
    """
    Takes gamelog data, scheduled matchups, and player data and creates input data for the projections model
    """

    def execute(
        self,
        gamelogs: list[GamelogEntity],
        scheduled_matchups: list[ScheduledMatchupEntity],
        players: list[PlayerEntity],
    ) -> list[ProjectionEntity]:
        """
        Forecasts player statistics, i.e. rebounds, points, for each player's games in the current week.

        :return: A dictionary of player weekly projections.
        :rtype: dict
        """

        active_players: list[PlayerEntity] = [player for player in players if player.team is not None]

        gamelogs_df: pd.DataFrame = pd.json_normalize([dict(gamelog) for gamelog in gamelogs])[
            [
                "playerId",
                "dateUTC",
                "position",
                "isStarter",
                "isActive",
                "playerTeam.teamId",
                "opposingTeam.teamId",
                "minutes",
                "fieldGoalsAttempted",
                "fieldGoalsMade",
                "freeThrowsAttempted",
                "freeThrowsMade",
                "points",
                "threesMade",
                "steals",
                "blocks",
                "assists",
                "reboundsTotal",
                "turnovers",
            ]
        ]
        gamelogs_df = gamelogs_df[gamelogs_df["isActive"]]  # Only include games where the player is active.
        gamelogs_df["dateUTC"] = pd.to_datetime(gamelogs_df["dateUTC"])  # Convert column to datetime.
        defense_df: pd.DataFrame = self._calculate_defensive_ratings(gamelogs_df)
        player_averages_df: pd.DataFrame = self._calculate_player_averages(players, gamelogs_df)
        current_datetime = pd.to_datetime(datetime.utcnow()).tz_localize("UTC")

        player_projections: list[ProjectionEntity] = []
        for player in active_players:
            player_scheduled_matchups: list[ScheduledMatchupEntity] = []
            for matchup in scheduled_matchups:
                matchup_datetime = pd.to_datetime(matchup.dateTimeUTC)
                is_home_player_team: bool = matchup.homeTeam.teamId == player.team.teamId
                is_away_player_team: bool = matchup.awayTeam.teamId == player.team.teamId

                if (is_home_player_team or is_away_player_team) and matchup_datetime > current_datetime:
                    player_scheduled_matchups.append(matchup)

            for schedule in player_scheduled_matchups:
                player_team: TeamEntity = schedule.homeTeam
                opposing_team: TeamEntity = schedule.awayTeam
                if schedule.awayTeam.teamId == player.team.teamId:
                    player_team = schedule.awayTeam
                    opposing_team = schedule.homeTeam

                is_starter: bool = player.depthChartOrder == 1
                is_injured: bool = False
                if player.injuryStatus is not None:
                    is_injured = player.injuryStatus.upper() == "OUT"

                player_game_projection: ProjectionEntity = None

                if not is_injured:
                    player_averages: pd.Series = player_averages_df.loc[player.playerId]
                    defense_ratings: pd.Series = defense_df.loc[(opposing_team.teamId, player.position, is_starter)]

                    predictions: list[float] = self._calculate_projections(player_averages, defense_ratings)
                    player_game_projection: ProjectionEntity = ProjectionEntity(
                        gameId=schedule.gameId,
                        dateUTC=schedule.dateTimeUTC,
                        playerId=player.playerId,
                        playerTeam=player_team,
                        opposingTeam=opposing_team,
                        fieldGoalsAttempted=predictions["fieldGoalsAttempted"],
                        fieldGoalsMade=predictions["fieldGoalsMade"],
                        threesMade=predictions["threesMade"],
                        freeThrowsAttempted=predictions["freeThrowsAttempted"],
                        freeThrowsMade=predictions["freeThrowsMade"],
                        points=predictions["points"],
                        assists=predictions["assists"],
                        rebounds=predictions["reboundsTotal"],
                        turnovers=predictions["turnovers"],
                        steals=predictions["steals"],
                        blocks=predictions["blocks"],
                    )
                else:
                    player_game_projection = ProjectionEntity(
                        gameId=schedule.gameId,
                        dateUTC=schedule.dateTimeUTC,
                        playerId=player.playerId,
                        playerTeam=player_team,
                        opposingTeam=opposing_team,
                        fieldGoalsAttempted=0,
                        fieldGoalsMade=0,
                        threesMade=0,
                        freeThrowsAttempted=0,
                        freeThrowsMade=0,
                        points=0,
                        assists=0,
                        rebounds=0,
                        turnovers=0,
                        steals=0,
                        blocks=0,
                    )
                player_projections.append(player_game_projection)

        return player_projections

    def _calculate_projections(self, player_averages: pd.Series, defense_ratings: pd.Series) -> dict[float]:
        """
        Calculate predicted player game stats based on player averages and defensive ratings.

        The formulas are multivariate linear regressions trained with machine learning.

        :param player_averages pd.Series: The player's statistical averages.
        :param defense_ratings pd.Series: The opposing team's defensive ratings,
            i.e. per-minute stats against the player's position.
        :return: A dictionary of predicted player game stats.
        :rtype: dict
        """

        field_goals_attempted: float = (
            -0.604 + 0.949 * player_averages["fieldGoalsAttempted"] + 2.956 * defense_ratings["fieldGoalsAttempted"]
        )
        field_goals_made: float = (
            -0.367 + 0.925 * player_averages["fieldGoalsMade"] + 3.902 * defense_ratings["fieldGoalsMade"]
        )
        threes_made: float = -0.02 + 0.856 * player_averages["threesMade"] + 3.39 * defense_ratings["threesMade"]
        free_throws_attempted: float = (
            -0.08 + 0.874 * player_averages["freeThrowsAttempted"] + 3.212 * defense_ratings["freeThrowsAttempted"]
        )
        free_throws_made: float = (
            -0.046 + 0.864 * player_averages["freeThrowsMade"] + 3.219 * defense_ratings["freeThrowsMade"]
        )
        points: float = -0.778 + 0.928 * player_averages["points"] + 3.307 * defense_ratings["points"]
        assists: float = -0.004 + 0.931 * player_averages["assists"] + 1.789 * defense_ratings["assists"]
        rebounds_total: float = (
            0.059 + 0.931 * player_averages["reboundsTotal"] + 1.392 * defense_ratings["reboundsTotal"]
        )
        turnovers: float = -0.018 + 0.846 * player_averages["turnovers"] + 3.354 * defense_ratings["turnovers"]
        steals: float = 0.171 + 0.714 * player_averages["steals"]
        blocks: float = 0.027 + 0.747 * player_averages["blocks"] + 3.439 * defense_ratings["blocks"]
        return {
            "fieldGoalsAttempted": field_goals_attempted,
            "fieldGoalsMade": field_goals_made,
            "threesMade": threes_made,
            "freeThrowsAttempted": free_throws_attempted,
            "freeThrowsMade": free_throws_made,
            "points": points,
            "assists": assists,
            "reboundsTotal": rebounds_total,
            "turnovers": turnovers,
            "steals": steals,
            "blocks": blocks,
        }

    def _calculate_player_averages(self, players: list[PlayerEntity], gamelogs_df: pd.DataFrame) -> dict:
        """
        Calculate statistical averages for a given player.

        :param player PlayerEntity: The player to calculate averages, i.e. points, rebounds average, for.
        :return: A dictionary of player averages.
        :rtype: dict
        """

        player_averages_df: pd.DataFrame = pd.DataFrame(
            columns=[
                "playerId",
                "playerTeam.teamId",
                "fieldGoalsAttempted",
                "fieldGoalsMade",
                "threesMade",
                "freeThrowsAttempted",
                "freeThrowsMade",
                "points",
                "assists",
                "reboundsTotal",
                "turnovers",
                "steals",
                "blocks",
            ]
        )

        current_datetime = pd.to_datetime(datetime.utcnow()).tz_localize("UTC")

        for player in players:
            player_id: int = -1
            if player.team is not None:
                player_id = player.team.teamId

            player_gamelogs_df: pd.DataFrame = gamelogs_df[
                (gamelogs_df["playerId"] == player.playerId) & (gamelogs_df["playerTeam.teamId"] == player_id)
            ]

            stats = {
                "fieldGoalsAttempted": 0,
                "fieldGoalsMade": 0,
                "threesMade": 0,
                "freeThrowsAttempted": 0,
                "freeThrowsMade": 0,
                "points": 0,
                "assists": 0,
                "reboundsTotal": 0,
                "turnovers": 0,
                "steals": 0,
                "blocks": 0,
            }

            is_starter: bool = player.depthChartOrder == 1  # Check if the player is a starter (1 on the depth chart).
            starter_filter = gamelogs_df["isStarter"] == is_starter  # Filter for the player's starter status.
            position_filter = gamelogs_df["position"] == player.position  # Filter for the player's position.
            player_id_filter = gamelogs_df["playerId"] == player.playerId  # Filter for the player's playerId.

            for stat in stats.keys():
                if is_starter:
                    player_start_games = player_gamelogs_df[player_gamelogs_df["isStarter"]]
                    if len(player_start_games) < 3:
                        stats[stat] = gamelogs_df[starter_filter & player_id_filter][stat].mean()
                    else:
                        weights = 0.98 ** (current_datetime - player_start_games["dateUTC"]).dt.days
                        stats[stat] = np.sum(weights * player_start_games[stat]) / np.sum(weights)
                else:
                    player_bench_games = player_gamelogs_df[~player_gamelogs_df["isStarter"]]
                    if len(player_bench_games) < 3:
                        stats[stat] = gamelogs_df[starter_filter & position_filter][stat].mean()
                    else:
                        weights = 0.98 ** (current_datetime - player_bench_games["dateUTC"]).dt.days
                        stats[stat] = np.sum(weights * player_bench_games[stat]) / np.sum(weights)

            stats["playerId"] = player.playerId
            player_averages_df.loc[len(player_averages_df)] = stats

        player_averages_df.set_index("playerId", inplace=True)
        return player_averages_df

    def _calculate_defensive_ratings(self, gamelogs_df: pd.DataFrame) -> pd.DataFrame:
        """
        This method calculates the defensive ratings against each position and whether the player is a starter.
        """

        recent_gamelogs = gamelogs_df[
            (gamelogs_df["dateUTC"] > pd.Timestamp(datetime.utcnow() - timedelta(days=50)).tz_localize("UTC"))
        ]

        if len(recent_gamelogs["dateUTC"].unique()) < 20:
            recent_gamelogs = gamelogs_df[(gamelogs_df["dateUTC"] < datetime.utcnow())]

        gamelogs_aggregate_df = recent_gamelogs.drop(
            columns=["dateUTC", "playerId", "isActive", "playerTeam.teamId"]
        ).groupby(["opposingTeam.teamId", "position", "isStarter"])

        defense_df = gamelogs_aggregate_df.sum().div(gamelogs_aggregate_df["minutes"].sum(), axis=0)

        return defense_df
