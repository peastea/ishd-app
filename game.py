from events import Goal, Penalty
from player import Player
from collections import Counter

from team import Team


def getseconds(time: str) -> int:
    m,s = time.split(':')
    return int(m)*60 + int(s)

class Game():
    def __init__(self, id, year, league, date, hometeam, awayteam, winner, lineup_home: list[(Player,int,str)], lineup_away : list[(Player,int,str)], goals : list[Goal], penalties : list[Penalty]):
        self.id = id
        self.year = year
        self.league = league
        self.date = date
        self.hometeam = hometeam
        self.awayteam = awayteam
        self.winner = winner
        self.lineup_home = lineup_home #Player, Number, Position
        self.lineup_away = lineup_away #Player, Number, Position
        self.goals = goals
        self.penalties = penalties
        self.powerplayhome = 0
        self.powerplayaway = 0
        self.__powerplaygoals = self.__calcpowerplay()        
        self.__writeppg()

    def get_year(self):
        return self.year 

    def get_id(self):
        return self.id
    
    def get_events(self):
        events = [(getseconds(g.get_time()), g) for g in self.goals]
        events.extend([(getseconds(p.get_time()), p) for p in self.penalties])
        events.sort(key=lambda x: x[0])
        return events

    def get_lineuphome(self):
        return self.lineup_home
    
    def get_lineupaway(self):
        return self.lineup_away

    def get_hometeam(self) -> Team:
        return self.hometeam

    def get_awayteam(self) -> Team:
        return self.awayteam

    def isplayerinlineup(self, player : Player) -> bool:
        lineup = self.lineup_home
        lineup.extend(self.lineup_away)
        for p, *_ in lineup:
            if p == player:
                return True
        return False

    def get_goals(self) -> list[Goal]:
        return self.goals

    ###### 
    # Goals
    ######

    def get_goalscorerlist(self) -> list[Player]: 
        """Returns a list of each goal scorer in the game."""
        return [goal.get_scorer() for goal in self.goals]

    def get_goalscorersorted(self) -> list[tuple[Player, int]]: 
        """Returns a sorted list with tuples of (Player, #OfGoals)"""       
        return Counter(self.get_goalscorerlist).most_common()

    def get_goalsbyplayer(self, player:Player) -> list[Goal]:
        return [g for g in self.goals if g.get_player() == player]

    def get_powerplaygoals(self) -> list[Goal]:
        return [goal for goal in self.goals if goal.get_isppg()]

    def __calcpowerplay(self) -> tuple[Goal,bool]:
        events = self.get_events()
        penaltieshome = [] #Tuple(seconds when expired, bool: True if 5 minute penalty)
        penaltiesaway = [] #Tuple(seconds when expired, bool: True if 5 minute penalty)
        ppg = []

        for time, event in events:
            # clear expired penalties
            for endtime, isfive in penaltieshome:
                if time > endtime:
                    penaltieshome.remove((endtime,isfive))
            for endtime, isfive in penaltiesaway:
                if time > endtime:
                    penaltiesaway.remove((endtime,isfive))

            # add penalty to list
            if isinstance(event, Penalty) and event.get_penaltyminutes() <= 5:
                if event.get_team() == self.hometeam:
                    penaltieshome.append((time + event.get_penaltyminutes() * 60, event.get_penaltyminutes == 5))
                elif  event.get_team() == self.awayteam:
                    penaltiesaway.append((time + event.get_penaltyminutes() * 60, event.get_penaltyminutes == 5))
            
            # check for power play goal
            if isinstance(event, Goal):
                isfiveminutes = True
                if event.get_team() == self.hometeam and len(penaltiesaway) > len(penaltieshome):                    
                    for endtime, isfive in penaltieshome:
                        if not isfive:
                            penaltieshome.remove((endtime, isfive))
                            isfiveminutes = False
                            break
                    ppg.append((event, isfiveminutes))
                if event.get_team() == self.awayteam and len(penaltieshome) > len(penaltiesaway):
                    for endtime, isfive in penaltiesaway:
                        if not isfive:
                            penaltiesaway.remove((endtime, isfive))
                            isfiveminutes = False
                            break
                    ppg.append((event, isfiveminutes))
        return ppg

    def __writeppg(self):    
        for goal in self.goals:
            goal.set_isppgduringfive(False)
            goal.set_isppg(False)
            for ppg, five in self.__powerplaygoals: 
                if goal == ppg:
                    goal.set_isppg(True)
                    goal.set_isppgduringfive(five)
                    break
                

    #TODO: 
    def get_powerplayhome(self) -> int:
        powerplay = 0
        for penalty in self.penalties:
            if penalty.get_team() == self.awayteam and penalty.get_penaltyminutes() <= 5:
                for p_same in self.penalties:
                    if p_same.get_team() != self.hometeam or penalty.get_time() != p_same.get_time():
                        powerplay += 1
        return powerplay

    ###### 
    # Assists
    ######

    def get_assistlist(self) -> list[Player]:
        """Returns a list of assisting player for each goal in the game."""
        return [penalty.get_player() for penalty in self.penalties]  
    
    def get_assistsorted(self):
        """Returns a sorted list with tuples of (Player, #OfPenalties)"""  
        return Counter(self.get_assistlist).most_common()   

    def get_assistsbyplayer(self, player:Player) -> list[Goal]:
        return [a for a in self.goals if a.get_assist() == player]
    
    ###### 
    # Points
    ######

    def get_pointlist(self) -> list[Player]:
        """Return a list of players for each point (goal or assist) in the game"""
        list = self.get_goalscorerlist()
        list.append(self.get_assistlist())
        return list

    def get_pointsorted(self) -> list[tuple[Player, int]]:
        """Returns a sorted list with tuples (Player, #OfPoints)"""
        return Counter(self.get_pointlist()).most_common()

    ###### 
    # Penalties
    ######

    def get_penalties(self) -> list[Penalty]:
        return self.penalties

    def get_penaltieshome(self) -> list[Penalty]:
        return [penalty for penalty in self.penalties if penalty.get_team() == self.hometeam]

    def get_penaltiesaway(self) -> list[Penalty]:
        return [penalty for penalty in self.penalties if penalty.get_team() == self.awayteam]

    def get_penaltyminutes(self) -> int:
        return sum([penalty.get_penaltyminutes() for penalty in self.penalties])

    def get_penaltyminuteshome(self) -> int:
        return sum([penalty.get_penaltyminutes() for penalty in self.get_penaltieshome])
    
    def get_penaltyminutesaway(self) -> int:
        return sum([penalty.get_penaltyminutes() for penalty in self.get_penaltiesaway])
    
    def get_penaltybyplayer(self, player:Player) -> list[Penalty]:
        return [p for p in self.penalties if p.get_player() == player]

    def get_penaltybyteam(self, team:Team) -> list[Penalty]:
        return [p for p in self.penalties if p.get_team() == team]

    def get_penaltyagainstteam(self, team:Team) -> list[Penalty]:
        return [p for p in self.penalties if p.get_team() != team]