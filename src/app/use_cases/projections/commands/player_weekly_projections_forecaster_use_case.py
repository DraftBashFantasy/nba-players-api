from datetime import datetime, timedelta
from src.interfaces.repositories import (
    IPlayerRepository,
    IGamelogRepository,
    IScheduledMatchupRepository,
    IProjectionRepository,
)
from src.interfaces.projections_model import IPlayerWeeklyProjectionsForecasterService
from src.domain.entities import ProjectionEntity, PlayerEntity, GamelogEntity, ScheduledMatchupEntity


class PlayerWeeklyProjectionsForecasterUseCase:
    """
    This class is responsible for forecasting weekly projections, i.e. rebounds, assists, etc., for games a player
    is scheduled to play in the upcoming week.

    :param player_repository IPlayerRepository: An instance of a player repository implementing its interface
    :param gamelog_repository IGamelogRepository: An instance of a gamelog repository implementing its interface
    :param scheduled_matchup_repository IScheduledMatchupRepository: An instance of a scheduled matchup repository 
        implementing its interface
    :param projection_repository IProjectionRepository: An instance of a projection repository 
        implementing its interface
    :param player_weekly_projections_forecaster_service IPlayerWeeklyProjectionsForecasterService: An instance of a
        player weekly projections forecaster service implementing its interface
    """

    def __init__(
        self,
        player_repository: IPlayerRepository,
        gamelog_repository: IGamelogRepository,
        scheduled_matchup_repository: IScheduledMatchupRepository,
        projection_repository: IProjectionRepository,
        player_weekly_projections_forecaster_service: IPlayerWeeklyProjectionsForecasterService,
    ):
        self._player_repository = player_repository
        self._gamelog_repository = gamelog_repository
        self._scheduled_matchup_repository = scheduled_matchup_repository
        self._projection_repository = projection_repository
        self._forecaster_service = player_weekly_projections_forecaster_service

    def execute(self) -> None:

        week_start: datetime = datetime.utcnow() - timedelta(days=(datetime.utcnow().weekday() - 0) % 7)
        week_finish: datetime = week_start + timedelta(days=7)
        players: list[PlayerEntity] = self._player_repository.get_all()
        gamelogs: list[GamelogEntity] = self._gamelog_repository.get_all_between_dates(
            datetime.utcnow() - timedelta(days=365), datetime.utcnow()
        )
        if len(gamelogs) > 0:
            matchups: list[ScheduledMatchupEntity] = self._scheduled_matchup_repository.get_matchups_between_dates(
                week_start, week_finish
            )

            projections: list[ProjectionEntity] = self._forecaster_service.execute(gamelogs, matchups, players)
            self._player_repository.upsert_many_projections(projections)
            self._projection_repository.upsert_many(projections)
