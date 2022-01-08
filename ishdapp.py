from flask import Flask, render_template, url_for, request
import sqlite3
import helper 
from collections import Counter
import os

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__) 
con = sqlite3.connect(os.path.join(THIS_FOLDER, 'DB/ishd-db.db'))
cur = con.cursor()
teams = helper.getallteams(cur)
players = helper.getallplayers(cur, teams)
games = helper.getallgames(cur, teams, players)
seasons = helper.getseasons(games)
cur.close()
con.close()  

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/team", methods=['GET', 'POST'])
def team():
    years=[season.get_year() for season in seasons]
    selectedyears = [str(season.get_year()) for season in seasons] #default
    selectedteam = 5 #default

    if request.method == 'POST':
        selectedyears = request.form.getlist('year')
        selectedteam = request.form.get('team')

    team = helper.getteamobject_byid(int(selectedteam),teams)
    goalsfor = helper.getamountperinterval([goal.get_time() for season in seasons for goal in season.get_goalsbyteam(team) if str(season.get_year()) in selectedyears])
    goalsagainst = [-x for x in helper.getamountperinterval([goal.get_time() for season in seasons for goal in season.get_goalsagainstteam(team) if str(season.get_year()) in selectedyears])]

    penaltiesby = helper.getamountperinterval([p.get_time() for season in seasons for p in season.get_penaltybyteam(team) if str(season.get_year()) in selectedyears and p.get_penaltyminutes() == 2])
    penaltiesdrawn = [-x for x in helper.getamountperinterval([p.get_time() for season in seasons for p in season.get_penaltyagainstteam(team)if str(season.get_year()) in selectedyears and p.get_penaltyminutes() == 2])]
    
    penaltytype = Counter([p.get_penaltytype() for season in seasons for p in season.get_penaltybyteam(team) if str(season.get_year()) in selectedyears]).most_common()
    
    points = []
    gamesplayed = []
    for player in players :
        if player.get_team() == team:
            goals = []
            assists = []
            games = []
            for season in seasons:
                if str(season.get_year()) in selectedyears:
                    goals.extend(season.get_goalsbyplayer(player))
                    assists.extend(season.get_assistsbyplayer(player))  
                    games.extend(season.get_gamesbyplayer(player))          
            points.append((player.get_fullname(), len(goals), len(assists)))    
            gamesplayed.append((player.get_fullname(),len(games)))    
    points.sort(key=lambda x:x[1]+x[2], reverse=True)
    points = points[:10]
    gamesplayed.sort(key=lambda x:x[1], reverse=True)
    gamesplayed = gamesplayed[:10]

    
    
    return render_template('team.html', currentteam=team, currentyears=selectedyears, teams=teams, times=helper.intervallong, years = years,
                            goalsfor=goalsfor, goalsagainst=goalsagainst,
                            penaltiesby=penaltiesby, penaltiesdrawn=penaltiesdrawn,
                            penaltynames=[name for name,_ in penaltytype], penaltynumber=[amount for _,amount in penaltytype],
                            pointsname=[n for n,*_ in points], playergoals=[g for _,g,_ in points], playerassists=[a for *_,a in points],
                            gpnames=[n for n,_ in gamesplayed], gamesplayed=[g for _,g in gamesplayed] )

@app.route("/player", methods=['GET','POST'])
def player():
    years=[season.get_year() for season in seasons]
    selectedyears = [str(season.get_year()) for season in seasons]  #default all season
    selectedplayer = helper.getplayerobject_byid(119, players) #default
    selectedseasons = seasons
    if request.method == 'POST':
        selectedyears = request.form.getlist('year')
        selectedplayer = helper.getplayerobject_byid(int(request.form.get('player')),players)
        selectedseasons = [s for s in seasons if str(s.get_year()) in selectedyears]

    players.sort(key=lambda x: x.get_fullname())

    games = [g for s in selectedseasons for g in s.get_gamesbyplayer(selectedplayer)]
    goals = [g for s in selectedseasons for g in s.get_goalsbyplayer(selectedplayer)]
    goalsinterval = helper.getamountperinterval([g.get_time() for g in goals])
    assists = [a for s in selectedseasons for a in s.get_assistsbyplayer(selectedplayer)]
    assistsinterval = helper.getamountperinterval([a.get_time() for a in assists])
    penalties = [p for s in selectedseasons for p in s.get_penaltybyplayer(selectedplayer)]
    penalties_plot = helper.getamountperinterval([p.get_time() for p in penalties])
    penaltymin = sum([p.get_penaltyminutes() for p in penalties])

    scorer = helper.gettopscorer(selectedseasons)
    goalpos = [p for p,_ in scorer].index(selectedplayer) + 1
    ass =  helper.gettopassists(selectedseasons)
    assistpos = [p for p,_ in ass].index(selectedplayer) + 1
    pen = helper.gettoppenalties(selectedseasons)
    penpos = [p for p,_ in pen].index(selectedplayer) +1

    return render_template('player.html', players=players, years=years, player=selectedplayer, selectedyears=selectedyears, times=helper.intervallong,
                            goalsinterval=goalsinterval, assistsinterval=assistsinterval, goals=goals, assists=assists,
                            penalties=penalties_plot, games=games, penaltymin = penaltymin, 
                            goalpos=goalpos, assistpos= assistpos)

@app.route("/league", methods=['GET','POST'])
def league():

    return render_template('league.html')

if __name__ == '__main__':
    app.run(debug=True)
    