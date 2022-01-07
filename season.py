from game import Game
from player import Player
from events import Goal, Penalty
from team import Team

class Season():
    def __init__(self, games: list[Game], year, league=None) -> None:
        self.games = games
        self.year = year
        self.league = league       
    

    def get_goalsbyplayer(self, player: Player) -> list[Goal]:
        goals = []
        for game in self.games:
            for goal in game.get_goalsbyplayer(player):
                goals.append(goal)
        return goals
    
    def get_goalsbyteam(self, team: Team) -> list[Goal]:
        return [goal for game in self.games for goal in game.get_goals() if goal.get_team() == team]
    
    def get_goalsagainstteam(self, team:Team) -> list[Goal]:
        return [goal for game in self.games for goal in game.get_goals() if (game.get_hometeam() == team or game.get_awayteam() == team) and goal.get_team() != team]

    def get_ppgbyplayer(self, player: Player) -> list[Goal]:
        return [goal for game in self.games for goal in game.get_powerplaygoals() if goal.get_player() == player]
    
    def get_ppgbyteam(self, team:Team) -> list[Goal]:
        return [goal for game in self.games for goal in game.get_powerplaygoals() if goal.get_team() == team]

    def get_ppgagainstteam(self, team:Team) -> list[Goal]:
        return [goal for game in self.games for goal in game.get_powerplaygoals() if (game.get_hometeam() == team or game.get_awayteam() == team) and goal.get_team() != team]
    
    def get_assistsbyplayer(self, player : Player) -> list[Goal]:
        return [a for game in self.games for a in game.get_assistsbyplayer(player)]

    def get_penaltybyplayer(self, player:Player) -> list[Penalty]:
        return [p for game in self.games for p in game.get_penaltybyplayer(player)]

    def get_penaltybyteam(self, team: Team) -> list[Penalty]:
        return [p for game in self.games for p in game.get_penaltybyteam(team)]
    
    def get_penaltyagainstteam(self, team: Team) -> list[Penalty]:
        return [p for game in self.games for p in game.get_penaltyagainstteam(team) if game.get_hometeam() == team or game.get_awayteam() == team]

    def get_year(self) -> int:
        return self.year

    def get_gamesbyplayer(self, player:Player) -> list[Game]:
        return [game for game in self.games if game.isplayerinlineup(player)]

    def get_gamesbyteam(self, team:Team) -> list[Game]:
        return [game for game in self.games if game.get_hometeam() == team or game.get_awayteam() == team] 
