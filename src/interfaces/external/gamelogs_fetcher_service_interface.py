from abc import ABC, abstractmethod
from domain.entities import GamelogEntity


class IGamelogsFetcher(ABC):
    """
    Fetches NBA player gamelogs according to the given game_ids.

    :param get_recent_game_ids: Gets the game_ids over the last 10 days
    :param get_season_game_ids: Gets the game_ids for a given season.
    :param execute: Fetches NBA player gamelogs according to the given game_ids.
    """
    
    @abstractmethod
    def get_new_gamelogs(self, game_ids: list[int]) -> list[GamelogEntity]:
        """
        Fetches NBA player gamelogs according to the given game_ids.

        :param game_ids list[int]: A list of game_ids for which to fetch gamelogs.
        :return: A list of gamelog entities for each given game_id
        :rtype: list[GamelogEntity]
        """

        pass

    @abstractmethod
    def get_recent_game_ids(self) -> list[int]:
        """
        Gets the game_ids over the last 10 days

        :return: A list of game_ids for the last 10 days.
        :rtype: list[int]
        """
        pass

    def get_season_game_ids(self, season: int) -> list[int]:
        """
        Gets the game_ids for a given season.

        :param season int: The season for which to get the game_ids, i.e. 2024 for the 2023-24 season.
        :return: A list of game_ids for the given season.
        :rtype: list[int]
        """
        pass