from src.domain.entities import ScheduledMatchupEntity
from src.interfaces.repositories import IScheduledMatchupRepository
from datetime import datetime, timedelta


class GetScheduledMatchupsUseCase:
    """
    This class is responsible for retrieving the current week's scheduled matchups from the database.

    :param team_schedule_repository IScheduledMatchupRepository: The repository for scheduled matchups.
    """

    def __init__(self, team_schedule_repository: IScheduledMatchupRepository):
        self.team_schedule_repository = team_schedule_repository
        
    def get_current_week(self) -> list[ScheduledMatchupEntity]:
        """
        This method is responsible for fetching the week's scheduled matchups from the database.

        :return: A list of scheduled matchups for the current week.
        :rtype: list[ScheduledMatchup]
        """

        # Get today's date
        today = datetime.utcnow()

        # Calculate the number of days until the previous Monday (0 = Monday, 1 = Tuesday, ..., 6 = Sunday)
        days_until_monday = (today.weekday() - 0) % 7
        week_start_date = today - timedelta(days=days_until_monday)
        week_finish_date = week_start_date + timedelta(days=7)

        current_week_scheduled_matchups = self.team_schedule_repository.get_matchups_between_dates(
            week_start_date, week_finish_date
        )
        return current_week_scheduled_matchups

    def get_all(self) -> list[ScheduledMatchupEntity]:
        """
        This method is responsible for fetching all scheduled matchups in the current season from the database.

        :return: A list of scheduled matchups for the current season.
        :rtype: list[ScheduledMatchup]
        """

        return self.team_schedule_repository.get_scheduled_matchups()
