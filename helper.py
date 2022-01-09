import math
from events import Goal, Penalty
from game import Game
from player import Player
from season import Season
from team import Team
import itertools
from collections import Counter

intervallong = ['0-5','5-10','10-15', '15-20', '20-25','25-30','30-35','35-40','40-45','45-50','50-55','55-60']
intervalshort = ['0','5','10', '15', '20','25','30','35','40','45','50','55']

def getamountperinterval(times, size=12) -> list[int]:
    interval = [0 for i in range(size)]
    for time in times:
        m, _ = time.split(':')
        index = math.floor(int(m) / (60/size))
        interval[index] = interval[index]+1
    return interval

def getPlayerID(cur, firstName, lastName, teamid):
    return getSingleQueryResult(cur.execute("SELECT player_ID FROM player WHERE first_name='"+firstName+"' AND last_name='"+lastName+"' AND team='"+str(teamid)+"'").fetchone())

def getPlayerName(cur, playerid):
    return cur.execute(f"SELECT first_name, last_name FROM player WHERE player_ID = '{playerid}' ").fetchone()

def getTeamID(cur, name):
    return getSingleQueryResult(cur.execute(f"SELECT team_ID FROM team WHERE name='{name}'").fetchone())

#returns player id
def findPlayer(cur, firstName, lastName, teamid):
    return getSingleQueryResult(cur.execute("SELECT player_ID FROM player WHERE first_name='"+firstName+"' AND last_name='"+lastName+"' AND team='"+str(teamid)+"'").fetchone())

#returns game id
def findGame(cur, season, league, date, homeid):
    return getSingleQueryResult(cur.execute("SELECT game_ID FROM game WHERE season='"+str(season)+"' AND league='"+league+"'AND date='"+str(date)+"'AND home='"+str(homeid)+"'").fetchone())

#returns complete event
def findEvent(cur, gameid, period, eventnr):
    return getSingleQueryResult(cur.execute("SELECT * FROM event WHERE game='"+str(gameid)+"' AND period='"+str(period)+"' AND eventnr='"+str(eventnr)+"'").fetchone())

def findTeam(cur, name):
    return getSingleQueryResult(cur.execute(f"SELECT team_ID FROM team WHERE name='{name}'").fetchone())

def getSingleQueryResult(query):
    if query is not None:
        query = query[0]
    return query

def getplayer(cur, id, team=None):
    playerInfo = cur.execute(f"SELECT first_name, last_name, team FROM player WHERE player_ID = '{id}' ").fetchone()
    if playerInfo is None:
        return None
    else:
        if team is None:
            team = getteam(cur,playerInfo[2])
        return Player(id, team, playerInfo[0], playerInfo[1])

def getteam(cur, id):
    teaminfo = getSingleQueryResult(cur.execute(f"SELECT name FROM team WHERE team_ID = '{id}'").fetchone())
    if teaminfo is None:
        return None
    else:
        return Team(id, teaminfo)

def getallteams(cur):
    """Returns a list of all teams in team table"""
    teaminfo = cur.execute(f"SELECT team_ID, name FROM TEAM").fetchall()
    return [Team(team[0], team[1]) for team in teaminfo]

def getallplayers(cur, teams):
    playerinfo = cur.execute(f"SELECT * FROM player").fetchall()
    players=[]
    for player in playerinfo:
        for team in teams:
            if player[3] == team.get_id():
                players.append(Player(player[0], player[1], player[2], team))

    return players

def getallgames(cur, teams: list[Team], players :list[Player]) -> list[Game]:
    gameinfo = cur.execute("SELECT * FROM game").fetchall()
    games=[]
    
    
    for game in gameinfo:
        hometeam = getteamobject_byid(game[4], teams)
        awayteam = getteamobject_byid(game[5], teams)
        winner = getteamobject_byid(game[6], teams)
        lineup_home = []
        lineup_away = []
        goals = []
        penalties = []
        
        #Get Players
        lineupinfo = cur.execute(f"SELECT * FROM lineup WHERE game = '{game[0]}'").fetchall()
        for playing in lineupinfo:
            player = getplayerobject_byid(playing[1], players)
            if player.get_team().get_id() == hometeam.get_id():
                lineup_home.append((player, playing[4], playing[3]))
            else:
                lineup_away.append((player, playing[4], playing[3]))

        #Get events
        eventinfo = cur.execute(f"SELECT * FROM event WHERE game = '{game[0]}'").fetchall()
        for event in eventinfo:
            if event[5] == 1:
                penalties.append(Penalty(event[14], getteamobject_byid(event[2], teams), getplayerobject_byid(event[1], players), event[3], event[4], event[6], event[11], event[7], event[8], event[9], event[10]))
            else:
                goals.append(Goal(event[14], getteamobject_byid(event[2], teams), getplayerobject_byid(event[1], players), getplayerobject_byid(event[13],players), event[3], event[4]))
 
        games.append(Game(game[0], game[1], game[2] ,game[3], hometeam, awayteam, winner, lineup_home, lineup_away, goals, penalties))
    return games

def getseasons(games: list[Game]) -> list[Season]:
    years = []
    seasonlist = []
    for game in games:
        years.append((game.get_year(), game))
    years.sort(key=lambda x : x[0])

    for key, group in itertools.groupby(years, lambda x : x[0]):
        seasonlist.append(Season([game for year, game in list(group)],key))    
    
    return seasonlist


def getteamobject_byid(id, teams: list[Team]) -> Team:
    for team in teams:
        if team.get_id() == id:
            return team
    return None

def getplayerobject_byid(id, players: list[Player]) -> Player:
    for player in players:
        if player.get_id() == id:
            return player    
    return None

def getgameobject_byid(id, games: list[Game]) -> Game:
    for game in games:
        if game.get_id() == id:
            return game
    return None

def gettopgamesplayed(seasons:list[Season]) -> list[(Player, int)]:
    gamesplayed = {}
    for season in seasons:
        for player, games in season.get_playersgamesplayed():
            if player in gamesplayed.keys():
                gamesplayed[player] += games
            else:
                gamesplayed.update({player:games})    
    gamesplayed = list(gamesplayed.items())
    return sorted(gamesplayed, key=lambda x: x[1], reverse=True)

def gettopscorer(seasons:list[Season]) -> list[(Player, int)]:
    goalscorer = []
    for season in seasons:
        goalscorer.extend([goal.get_player() for goal in season.get_goals()])
    return Counter(goalscorer).most_common()

def gettopassists(seasons:list[Season]) -> list[(Player, int)]:
    assists = []
    for season in seasons:
        assists.extend([goal.get_assist() for goal in season.get_goals() if goal.get_assist() is not None])
    return Counter(assists).most_common()

def gettoppenalties(seasons:list[Season]) -> list[(Player, int)]:    
    penminutes = {}
    for season in seasons:
        for player in season.get_players():
            minutes = sum([p.get_penaltyminutes() for p in season.get_penaltybyplayer(player)])
            if player in penminutes.keys():
                penminutes[player] += minutes
            else:
                penminutes.update({player: minutes})

    penalties = list(penminutes.items())
    penalties.sort(key=lambda x: x[1], reverse=True)
    return penalties

def gettopgwg(seasons:list[Season]) -> list[(Player, int)]:
    gwgscorer = [goal.get_player() for s in seasons for goal in s.get_gamewinninggoals()]
    return Counter(gwgscorer).most_common()

def getoverallplace(player, listofplayer):
    if player in listofplayer:
        return listofplayer.index(player) + 1
    return None
