from player import Player
from team import Team

class Goal:
    def __init__ (self, id, team:Team, player:Player, assist:Player, time, period, isppg:bool=None, isppgduringfive:bool= None):
        self.id = id
        self.player = player
        self.team = team
        self.assist = assist
        self.time = time
        self.period = period
        self.isppg = isppg 
        self.isppgduringfive = isppgduringfive

    def set_isppg(self, isppg:bool):
        self.isppg = isppg
    
    def set_isppgduringfive(self, isduringfive:bool):
        self.isppgduringfive = isduringfive

    def get_isppg(self) -> bool:
        return self.isppg

    def get_isppgduringfive(self) -> bool:
        return self.isppgduringfive

    def get_player(self):
        return self.player

    def get_assist(self):
        return self.assist

    def get_team(self):
        return self.team

    def get_time(self):
        return self.time

    def get_id(self):
        return self.id

class Penalty:
    def __init__ (self, id, team, player, time, period, penaltyminutes, penaltytype, is_misconduct, is_game_misconduct, is_matchpenalty, is_suspension):
        self.id = id
        self.player = player
        self.team = team
        self.time = time
        self.period = period
        self.penaltyminutes = penaltyminutes
        self.penaltytype = penaltytype
        self.is_misconduct = is_misconduct
        self.is_game_misconduct = is_game_misconduct
        self.is_matchpenalty = is_matchpenalty
        self.is_suspension = is_suspension

    def get_player(self):
        return self.player
    
    def get_team(self):
        return self.team

    def get_penaltyminutes(self):
        return self.penaltyminutes

    def get_penaltytype(self):
        return self.penaltytype

    def get_time(self):
        return self.time
