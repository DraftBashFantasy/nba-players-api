from src.domain.entities import GamelogEntity
from src.interfaces.repositories import IGamelogRepository
from src.interfaces.external import IGamelogsFetcher


class GamelogsUpserterUseCase:
    """
    This class is responsible for upserting gamelogs into the database

    :param gamelog_repository IGamelogRepository: An instance of a gamelog repository implementing its interface
    """

    def __init__(self, gamelog_repository: IGamelogRepository, gamelogs_fetcher: IGamelogsFetcher):
        self.gamelog_repository = gamelog_repository
        self.gamelogs_fetcher = gamelogs_fetcher

    def execute(self, season) -> None:
        """
        Upserts the players into the database.
        
        :param season int: The season to fetch gamelogs for
        """

        game_ids: list[int] = []
        if season is None:
            game_ids = self.gamelogs_fetcher.get_recent_game_ids()
        else:
            game_ids = self.gamelogs_fetcher.get_season_game_ids(season)

        gamelogs: list[GamelogEntity] = self.gamelogs_fetcher.get_new_gamelogs(game_ids)

        self.gamelog_repository.upsert_many(gamelogs)