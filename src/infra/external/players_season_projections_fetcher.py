import requests
from bs4 import BeautifulSoup


class PlayersSeasonProjectionsFetcher:
    """
    Fetches season projections for NBA players.

    This class fetches NBA player season projected totals like total games played and points scored,
    as well as projected rankings for points and category leagues.
    """

    def fetch_projections(self) -> list[dict]:
        """
        Fetches the season projections for NBA players.

        :return: A list of dictionaries containing the season projections for NBA players.
        :rtype: list[dict]
        :raises Exception: If there's an error during the web scraping process.
        """

        # Get the player ranking dictionaries for category and points leagues
        category_rankings = self._fetch_category_rankings()

        points_rankings = self._fetch_points_rankings()

        # Scrape the player season projections from fantasypros.com
        URL = "https://www.fantasypros.com/nba/projections/overall.php"
        player_season_projections_response = requests.get(URL)
        soup = BeautifulSoup(player_season_projections_response.text, "html.parser")
        table_body = soup.find(class_="mobile-table").find("tbody")
        player_projections_rows = table_body.find_all("tr")

        # Parse the player season projections html into a list of season projections
        players_season_projections = []
        for player_projections_row in player_projections_rows:
            values = player_projections_row.find_all("td")
            fantasypros_player_id = values[0].find("a").get("class")[2].split("-")[2]
            points_league_ranking = points_rankings.get(fantasypros_player_id, None)
            category_league_ranking = category_rankings.get(fantasypros_player_id, None)
            players_season_projections.append(
                {
                    "pointsLeagueRanking": points_league_ranking,
                    "categoryLeagueRanking": category_league_ranking,
                    "firstName": values[0].find("a").text.split(" ")[0],
                    "lastName": values[0].find("a").text.split(" ")[1],
                    "teamAbbreviation": values[0].find("small").text[1:4],
                    "gamesPlayed": int(values[9].text.replace(",", "")),
                    "minutes": float(values[10].text.replace(",", "")),
                    "fieldGoalPercentage": float(values[6].text.replace(",", "")),
                    "threesMade": int(values[8].text.replace(",", "")),
                    "points": int(values[1].text.replace(",", "")),
                    "steals": int(values[5].text.replace(",", "")),
                    "blocks": int(values[4].text.replace(",", "")),
                    "assists": int(values[3].text.replace(",", "")),
                    "rebounds": int(values[2].text.replace(",", "")),
                    "turnovers": int(values[11].text.replace(",", "")),
                    "freeThrowPercentage": float(values[7].text.replace(",", "")),
                }
            )

        return players_season_projections

    def _fetch_category_rankings(self) -> list[dict]:
        """
        Fetch the category league rankings for NBA players.

        Webscrapes from fantasypros.com the current projected category league rankings for NBA players.

        :return: A dictionary mapping fantasypros.com's player ids to their category league rankings.
        :rtype: dict
        :raises Exception: If there's an error during the web scraping process.
        """

        # Webscrape the projected category league player rankings so that
        # we can include it in the season projects.
        rankings = {}
        try:
            URL = "https://www.fantasypros.com/nba/rankings/overall.php"
            html_response = requests.get(URL)
            soup = BeautifulSoup(html_response.text, "html.parser")
            table_rows = soup.find(class_="mobile-table").find("tbody").find_all("tr")
            for row in table_rows:
                values = row.find_all("td")
                fantasypros_player_id = values[1].find("a").get("fp-player-id")
                ranking = int(values[0].text.replace(",", ""))
                rankings[fantasypros_player_id] = ranking  # Maps player id to ranking

        except Exception as e:
            return rankings

        return rankings

    def _fetch_points_rankings(self) -> list[dict]:
        """
        Fetch the points league rankings for NBA players.

        Webscrapes from fantasypros.com the current projected points league rankings for NBA players.

        :return: A dictionary mapping fantasypros.com's player ids to their category league rankings.
        :rtype: dict
        :raises Exception: If there's an error during the web scraping process.
        """

        # Webscrape the projected category league player rankings so that
        # we can include it in the season projects.
        rankings = {}
        try:
            URL = "https://www.fantasypros.com/nba/rankings/overall-points-cbs.php"
            html_response = requests.get(URL)
            soup = BeautifulSoup(html_response.text, "html.parser")
            table_rows = soup.find(class_="mobile-table").find("tbody").find_all("tr")
            for row in table_rows:
                values = row.find_all("td")
                fantasypros_player_id = values[1].find("a").get("fp-player-id")
                ranking = int(values[0].text.replace(",", ""))
                rankings[fantasypros_player_id] = ranking  # Maps player id to ranking

        except Exception as e:
            return rankings

        return rankings
