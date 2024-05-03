from domain.entities import PlayerEntity
from interfaces.repositories import IPlayerRepository
from interfaces.external import IPlayersFetcher


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

        players: list[PlayerEntity] = self.playersFetcher.fetch_new_player_data()
        
        self.player_repository.upsert_many(players)
