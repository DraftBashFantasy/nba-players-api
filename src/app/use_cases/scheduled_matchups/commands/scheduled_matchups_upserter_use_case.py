from src.domain.entities import ScheduledMatchupEntity
from src.interfaces.repositories import IScheduledMatchupRepository
from src.interfaces.external import IScheduledMatchupsFetcherService


class ScheduledMatchupsUpserterUseCase:
    """
    This class is responsible for updating the week's scheduled matchups into the database.

    :param team_schedule_repository IScheduledMatchupRepository: The repository for scheduled matchups.
    :param scheduled_matchups_fetcher_service IScheduledMatchupsFetcherService: The service for fetching scheduled matchups.
    """

    def __init__(
        self,
        scheduled_matchup_repository: IScheduledMatchupRepository,
        scheduled_matchups_fetcher_service: IScheduledMatchupsFetcherService,
    ):
        self._scheduled_matchup_repository = scheduled_matchup_repository
        self._scheduled_matchups_fetcher_service = scheduled_matchups_fetcher_service

    def execute(self) -> None:
        """
        This method is responsible for upserting the week's scheduled matchups into the database.
        """

        scheduled_matchups: list[ScheduledMatchupEntity] = self._scheduled_matchups_fetcher_service.execute()

        self._scheduled_matchup_repository.upsert_many(scheduled_matchups)