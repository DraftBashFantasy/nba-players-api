from domain.entities import TeamEntity
from interfaces.external import ITeamsFetcherService


class TeamsFetcher(ITeamsFetcherService):
    """
    This class is responsible for fetching NBA teams.
    """

    def execute(self) -> list[TeamEntity]:
        """
        This method is responsible for fetching the teams.
        
        :return: list[TeamEntity]
        """

        # We will ultimately fetch the teams from the NBA API, but for now we will return a hardcoded list of teams
        nba_teams: list[TeamEntity] = [
            TeamEntity(name="Hawks", location="Atlanta", abbreviation="ATL", teamId="1610612737"),
            TeamEntity(name="Celtics", location="Boston", abbreviation="BOS", teamId="1610612738"),
            TeamEntity(name="Nets", location="Brooklyn", abbreviation="BKN", teamId="1610612751"),
            TeamEntity(name="Hornets", location="Charlotte", abbreviation="CHA", teamId="1610612766"),
            TeamEntity(name="Bulls", location="Chicago", abbreviation="CHI", teamId="1610612741"),
            TeamEntity(name="Cavaliers", location="Cleveland", abbreviation="CLE", teamId="1610612739"),
            TeamEntity(name="Mavericks", location="Dallas", abbreviation="DAL", teamId="1610612742"),
            TeamEntity(name="Nuggets", location="Denver", abbreviation="DEN", teamId="1610612743"),
            TeamEntity(name="Pistons", location="Detroit", abbreviation="DET", teamId="1610612765"),
            TeamEntity(name="Warriors", location="Golden State", abbreviation="GSW", teamId="1610612744"),
            TeamEntity(name="Rockets", location="Houston", abbreviation="HOU", teamId="1610612745"),
            TeamEntity(name="Pacers", location="Indiana", abbreviation="IND", teamId="1610612754"),
            TeamEntity(name="Clippers", location="Los Angeles", abbreviation="LAC", teamId="1610612746"),
            TeamEntity(name="Lakers", location="Los Angeles", abbreviation="LAL", teamId="1610612747"),
            TeamEntity(name="Grizzlies", location="Memphis", abbreviation="MEM", teamId="1610612763"),
            TeamEntity(name="Heat", location="Miami", abbreviation="MIA", teamId="1610612748"),
            TeamEntity(name="Bucks", location="Milwaukee", abbreviation="MIL", teamId="1610612749"),
            TeamEntity(name="Timberwolves", location="Minneapolis", abbreviation="MIN", teamId="1610612750"),
            TeamEntity(name="Pelicans", location="New Orleans", abbreviation="NOP", teamId="1610612740"),
            TeamEntity(name="Knicks", location="New York", abbreviation="NYK", teamId="1610612752"),
            TeamEntity(name="Thunder", location="Oklahoma City", abbreviation="OKC", teamId="1610612760"),
            TeamEntity(name="Magic", location="Orlando", abbreviation="ORL", teamId="1610612753"),
            TeamEntity(name="76ers", location="Philadelphia", abbreviation="PHI", teamId="1610612755"),
            TeamEntity(name="Suns", location="Phoenix", abbreviation="PHX", teamId="1610612756"),
            TeamEntity(name="Blazers", location="Portland", abbreviation="POR", teamId="1610612757"),
            TeamEntity(name="Kings", location="Sacramento", abbreviation="SAC", teamId="1610612758"),
            TeamEntity(name="Spurs", location="San Antonio", abbreviation="SAS", teamId="1610612759"),
            TeamEntity(name="Raptors", location="Toronto", abbreviation="TOR", teamId="1610612761"),
            TeamEntity(name="Jazz", location="Utah", abbreviation="UTA", teamId="1610612762"),
            TeamEntity(name="Wizards", location="Washington", abbreviation="WAS", teamId="1610612764"),
        ]

        return nba_teams
