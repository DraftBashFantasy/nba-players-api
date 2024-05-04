from src.domain.entities import PlayerEntity
from src.domain.value_objects.player_season_totals import PlayerSeasonTotals
from src.interfaces.repositories import IPlayerRepository
from src.interfaces.external import IPlayersFetcher
from datetime import datetime


class PlayersUpserterUseCase():
    """ This class is responsible for upserting players into the database
    
    :param player_repository IPlayerRepository: An instance of a player repository implementing its interface
    """

    def __init__(self, player_repository: IPlayerRepository, playersFetcher: IPlayersFetcher):
        self.player_repository = player_repository
        self.playersFetcher = playersFetcher

    def execute(self) -> None:
        """ 
        Upserts the players into the database. 
        """

        current_season: datetime = datetime.utcnow().year - 1
        if datetime.now().month >= 10:
            current_season = current_season

        players: list[PlayerEntity] = self.playersFetcher.execute()
        player_totals: dict = self.player_repository.get_season_totals(current_season)
        for player in players:
            try:
                player.seasonTotals = PlayerSeasonTotals(**player_totals[player.playerId])
            except KeyError:
                continue

        self.player_repository.upsert_many(players)
