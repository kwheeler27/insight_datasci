import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB

#connect to MySQL
def connect():
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root')
  db.autocommit(True)
  return db, db.cursor()

#returns the display name of the given player with the format: 'first-last'
def display_name(name):
  return name.lower().replace(' ','-')

#returns an int representing the week number selected
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
  command = "SELECT plyr_id FROM players WHERE name = '%s' LIMIT 1;" % (name)
  cur.execute(command)
  rows = cur.fetchall()
  return int(rows[0][0])

def convert_names_to_ids(cur, plyr_arr):
  id_arr = []
  for p in plyr_arr:
    id = player_id(cur, p)
    id_arr.append(id)
  return id_arr

def all_player_ids(cur):
  arr = []
  command = "SELECT DISTINCT(plyr_id) FROM matchups;"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  return np.array(arr)

def games_played_in(cur, id):
  arr = []
  command = "SELECT DISTINCT(game_id) FROM matchups WHERE plyr_id = '%s';" % (id)
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  return np.array(arr)

#returns an np.array (1D) of the players appearing in the given game
def plyrs_in_game(cur, game_id):
  arr = []
  command = "SELECT DISTINCT(plyr_id) FROM matchups WHERE game_id = '%s';" % (game_id)
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  return np.array(arr)

def update_training_matrix(plyrs_in_game, game, X):
  for p in plyrs_in_game:
    if p in X.ix[game]:
      X.ix[game][p] = 1
  return
    
def populate_training_set(cur, X, games):
  for g in games:
    plyrs = plyrs_in_game(cur, g) #np.arr - list of players who played in given game
    update_training_matrix(plyrs, g, X)
  return

def discretize(arr):
  result = []
  for i in arr:
    if i <= 3.0:
      result.append(0)
    elif i > 3.0 and i <= 6.0:
      result.append(1)
    elif i > 6.0 and i <= 9.0:
      result.append(2)
    elif i > 9.0 and i <= 12.0:
      result.append(3)       
    elif i > 12.0 and i <= 15.0:
      result.append(4)
    elif i > 15.0 and i <= 18.0:
      result.append(5)
    elif i > 18 and i <= 21.0:
      result.append(6)
    elif i > 21.0 and i <= 24.0:
      result.append(7)       
    elif i > 24.0 and i <= 27.0:
      result.append(8)
    elif i > 27.0 and i <= 30.0:
      result.append(9)
    else:
      result.append(10)
  return np.array(result) 
  
#returns an np.array (1D) of the fantasy scores for a given player
def training_output_vector(cur, games, plyr_id):
  arr = []
  for g in games:
    command = "SELECT fntsy_pts FROM fantasy_scores WHERE game_id = '%s' AND plyr_id = '%s';" % (g, plyr_id)
    cur.execute(command)
    rows = cur.fetchall()
    arr.append(rows[0][0])
  y = discretize(arr)
  return y

def normalize_probs(arr):
  norm = arr.sum()
  return np.divide(arr, norm)

def expected_val(nb_norm_prob, vals):
  ans = 0
  for i in xrange(nb_norm_prob.shape[0]):
    ans += nb_norm_prob[i]*vals[i]
  return ans
  
def predict(cur, plyr_id, game_plyrs): 
  #creates training set (called 'X') for plyr
  all_plyrs = all_player_ids(cur) #np.array - all NFL players
  games = games_played_in(cur, plyr_id) #np.array - the games_ids the player played in
  n_cols = all_plyrs.shape[0] #int
  m_rows = games.shape[0] #int
  zeros = np.zeros((m_rows, n_cols)) #2darr - used to initialize DF
  X = pd.DataFrame(zeros, index=games, columns=all_plyrs) #dataframe
  populate_training_set(cur, X, games)
  
  #creates vector of known output values
  Y = training_output_vector(cur, games, plyr_id)
  
  test_zeros = np.zeros((1, n_cols)) #2darr - used to initialize DF
  test_X = pd.DataFrame(zeros, columns=all_plyrs) #dataframe

  update_training_matrix(game_plyrs, 0, test_X)
  
  
  #run Bernoulli NB Classifier
  nb_clf = BernoulliNB()
  nb_clf.fit(X, Y)
  nb_predictions = nb_clf.predict(test_X)
  
  nb_norm_prob = normalize_probs(nb_clf.predict_proba(test_X)[0])
  avgs = [1.5, 4.5, 7.5, 10.5, 13.5, 16.5, 19.5, 22.5, 25.5, 28.5, 31.5]
  ev = expected_val(nb_norm_prob, avgs) 
  return round(ev, 2)
  
def make_predictions(plyrs, week_num):
  db = connect()[0]
  cur = connect()[1]
  predictions = {}
  
  for p in plyrs:
    disp_name = display_name(p)
    pos = plyr_position(cur, disp_name)
    id = player_id(cur, disp_name)
    name = disp_name.replace('-',' ').title()
    print name, pos
    
    game_plyrs = all_players(cur, disp_name, week_num)  
    plyr_ids = convert_names_to_ids(cur, game_plyrs)
    img_url = "http://s3-us-west-2.amazonaws.com/nflheadshots/%s-%s.png" % (id, disp_name)
    pts = predict(cur, id, plyr_ids)
    plyr_dict = {}
    plyr_dict[name] = (pts, img_url)
    if pos in predictions:
      predictions[pos].append(plyr_dict)
    else:
      predictions[pos] = []
      predictions[pos].append(plyr_dict)
    print predictions
  cur.close()
  del cur
  db.close()
  del db  
  return predictions
  
  
  