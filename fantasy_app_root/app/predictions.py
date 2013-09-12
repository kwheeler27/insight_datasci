import MySQLdb as mdb
import numpy as np

#connect to MySQL
def connect():
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root')
  db.autocommit(True)
  return db, db.cursor()

#returns the display name of the given player with the format: 'first-last'
def display_name(name):
  return name.lower().replace(' ','-')

#returns the week number selected
def get_week(form):
  return int(form['week'][1])

#returns an array of the players contained in the roster form
def plyr_names(form):
  plyr_arr = ['p1', 'p2', 'p3','p4','p5','p6', 'p7', 'p8','p9','p10','p11', 'p12', 'p13','p14','p15','p16', 'p17', 'p18','p19','p20']
  names = []
  for p in plyr_arr:
    val = form[p]
    if len(val) != 0:
      names.append(form[p].encode('ascii', 'ignore'))
  return names

#returns the team abbreviation that a given player plays for
def get_team(cur, plyr):
  command = "SELECT team FROM players WHERE name = '%s' LIMIT 1;" % (plyr)
  cur.execute(command)
  rows = cur.fetchall()
  plyr_team = rows[0][0]
  return plyr_team

#returns a given team's opponent for a given week
def get_opp_team(cur, plyr_team, week):
  command = "SELECT away FROM schedules WHERE home = '%s' AND week = '%s' LIMIT 1;" % (plyr_team, week)
  cur.execute(command)
  rows = cur.fetchall()
  opp_team = rows[0][0]
  return opp_team

#returns the list of players on a given team
def team_roster(cur, team):
  roster = []
  command = "SELECT DISTINCT(name) FROM players WHERE team = '%s';" % (team)
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    roster.append(r[0])
  return roster
  
#return an array of a player's opponents for a given week
def all_players(cur, plyr_name, week):
  home_team = get_team(cur, plyr_name)
  away_team = get_opp_team(cur, home_team, week)
  home_roster = team_roster(cur, home_team)
  away_roster = team_roster(cur, away_team)
  #print "HOME ROSTER: ", home_roster
  #print "OPP ROSTER: ", away_roster
  all_plyrs = home_roster + away_roster
  #print "TOT ROSTER: ",all_plyrs
  return all_plyrs

#returns a player's position
def plyr_position(cur, name):
  command = "SELECT position FROM players WHERE name = '%s' LIMIT 1;" % (name)
  cur.execute(command)
  rows = cur.fetchall()
  pos = rows[0][0]
  return pos

def player_id(cur, name):
  command = "SELECT plyr_id FROM players WHERE name = '%s' LIMIT 1;" % (p)
  cur.execute(command)
  rows = cur.fetchall()
  return int(rows[0][0])

def convert_names_to_ids(cur, plyr_arr):
  id_arr = []
  for p in plyr_arr:
    id = player_id(cur, p)
    id_arr.append(id)
  return id_arr

def 


def make_predictions(plyrs, week_num):
  db = connect()[0]
  cur = connect()[1]
  predictions = {}
  
  for p in plyrs:
    name = display_name(p)
    pos = plyr_position(cur, name)
    id = player_id(cur, name)
    print name, pos
    game_plyrs = all_players(cur, name, week_num)  
    plyr_ids = convert_names_to_ids(cur, game_plyrs)
    #test_x = construct_test_vec(
    
    pts = predict(cur, id, game_plyrs)
    plyr_dict = {}
    plyr_dict[name] = pts
    if pos in predictions:
      predictions[pos].append(plyr_dict)
    else:
      predictions[pos] = []
      predictions[pos].append(plyr_dict)
    
  cur.close()
  del cur
  db.close()
  del db  
  return {} #predictions
  
  
  