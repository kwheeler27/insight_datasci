import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB

#connect to MySQL
def connect():
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root', passwd='r')
  db.autocommit(True)
  return db, db.cursor()

#returns the display name of the given player with the format: 'first-last'
def display_name(name):
  return name.lower().replace(' ','-')

#returns an int representing the week number selected
def get_week(form):
  return int(form['week'][1:])

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
  command = "SELECT team FROM players WHERE name = '%s' LIMIT 1;" % (mdb.escape_string(plyr))
  cur.execute(command)
  rows = cur.fetchall()
  plyr_team = rows[0][0]
  return plyr_team

#returns a given team's opponent for a given week
def get_opp_team(cur, plyr_team, week):
  command = "SELECT away FROM schedules WHERE home = '%s' AND week = '%s' LIMIT 1;" % (plyr_team, week)
  cur.execute(command)
  rows = cur.fetchall()
  if len(rows) > 0:
    opp_team = rows[0][0]
    return opp_team
  else:
    return []

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
  if len(away_team) == 0:
    return []
  home_roster = team_roster(cur, home_team)
  away_roster = team_roster(cur, away_team)
  #print "HOME ROSTER: ", home_roster
  #print "OPP ROSTER: ", away_roster
  all_plyrs = home_roster + away_roster
  #print "TOT ROSTER: ",all_plyrs
  return all_plyrs

#returns a player's position
def plyr_position(cur, name):
  if name == 'dummy':
    return 'NA'
  command = "SELECT position FROM players WHERE name = '%s' LIMIT 1;" % (mdb.escape_string(name))
  cur.execute(command)
  rows = cur.fetchall()
  pos = rows[0][0]
  return pos

def player_id(cur, name):
  if name == 'dummy':
    return 0
  command = "SELECT plyr_id FROM players WHERE name = '%s' LIMIT 1;" % (mdb.escape_string(name))
  cur.execute(command)
  rows = cur.fetchall()
  return int(rows[0][0])

def convert_names_to_ids(cur, plyr_arr):
  id_arr = []
  for p in plyr_arr:
    id = player_id(cur, p)
    id_arr.append(id)
  return id_arr

#includes coach IDs
def all_player_ids(cur):
  arr = []
  command = "SELECT DISTINCT(plyr_id) FROM matchups;"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  
  command2 = "SELECT DISTINCT(coach_id) FROM coaches;"
  cur.execute(command2)
  rows2 = cur.fetchall()
  for r in rows2:
    arr.append(r[0])
  arr.append(99999) #code for starter col
  return np.array(arr)

def games_played_in(cur, id):
  arr = []
  command = "SELECT game_id FROM fantasy_scores WHERE plyr_id = '%s';" % (id)
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  return np.array(arr)

#returns an np.array (1D) of the players and coaches appearing in the given game and 
def plyrs_in_game(cur, game_id, plyr_id):
  #players
  arr = []
  command = "SELECT DISTINCT(plyr_id) FROM matchups WHERE game_id = '%s';" % (game_id)
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    arr.append(r[0])
  
  #coaches
  command2 = "SELECT coach_id FROM coaches WHERE game_id = '%s';" % (game_id)
  cur.execute(command2)
  rows2 = cur.fetchall()
  for r in rows2:
    arr.append(r[0])
  
  #starter?
  command3 = "SELECT is_starter FROM past_starters WHERE game_id = '%s' AND plyr_id = '%s';" % (game_id, plyr_id)
  cur.execute(command3)
  rows3 = cur.fetchall()
  for r in rows3:
    starter = r[0]
    if starter == 1:
      arr.append(99999)
  return np.array(arr)

#sets X[game_id][plyr_id] = 1 if plyr/coach is in plyrs_in_game
def update_training_matrix(plyrs_in_game, game, X):
  if len(X.values) == 0:
    return
  for p in plyrs_in_game:
    if p in X.ix[game]:
      X.ix[game][p] = 1
  return

#populates an empty training matrix, X    
def populate_training_set(cur, X, games, plyr_id):
  for g in games:
    plyrs = plyrs_in_game(cur, g, plyr_id) #np.arr - list of players who played in given game (incls coaches/starter)
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
  print "Y - before discretize", arr
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
  all_plyrs = all_player_ids(cur) #np.array - all NFL players (and coaches)
  games = games_played_in(cur, plyr_id) #np.array - the games_ids the player played in
  n_cols = all_plyrs.shape[0] #int 
  m_rows = games.shape[0] #int
  zeros = np.zeros((m_rows, n_cols)) #2darr - used to initialize DF
  X = pd.DataFrame(zeros, index=games, columns=all_plyrs) #dataframe
  populate_training_set(cur, X, games, plyr_id)
  print "X: ", X.values
  
  
  #creates vector of known output values
  Y = training_output_vector(cur, games, plyr_id)
  print "(len) Y: ", len(Y), Y
  test_zeros = np.zeros((1, n_cols)) #2darr - used to initialize DF
  test_X = pd.DataFrame(zeros, columns=all_plyrs) #dataframe
  update_training_matrix(game_plyrs, 0, test_X)
  
  #run Bernoulli NB Classifier
  nb_clf = BernoulliNB()
  
  if len(X.values) == 0:
    return 0
  nb_clf.fit(X, Y)
  nb_predictions = nb_clf.predict(test_X)
  print "test_X: ", test_X.values
  nb_norm_prob = normalize_probs(nb_clf.predict_proba(test_X)[0])
  avgs = [1.5, 4.5, 7.5, 10.5, 13.5, 16.5, 19.5, 22.5, 25.5, 28.5, 31.5]
  print "param vector: ", nb_clf.predict_proba(test_X)[0]
  print "probs: ", nb_norm_prob
  print avgs
  ev = expected_val(nb_norm_prob, avgs) #can also calc dot product
  return round(ev, 1)
  
#returns coach id given team abbr
def coach(team):
  coach_dict = {}
  coach_dict['buf'] = [80,81,81,81,105]
  coach_dict['mia'] = [65,65,65,97,97]
  coach_dict['ne'] = [2,2,2,2,2]
  coach_dict['nyj'] = [72,72,72,72,72]
  coach_dict['den'] = [73,73,13,13,13]
  coach_dict['kc'] = [77,77,77,49,23]
  coach_dict['oak'] = [69,69,69,98,98]
  coach_dict['sd'] = [44,44,44,44,44]
  coach_dict['bal'] = [68,68,68,68,68]
  coach_dict['cin'] = [18,18,18,18,18]
  coach_dict['cle'] = [54,54,92,92,101]
  coach_dict['pit'] = [63,63,63,63,63]
  coach_dict['hou'] = [56,56,56,56,56]
  coach_dict['ind'] = [76,76,76,99,99]
  coach_dict['jac'] = [5,5,5,43,108]
  coach_dict['ten'] = [12,12,94,94,94]
  coach_dict['dal'] = [85,85,85,85,85]
  coach_dict['nyg'] = [35,35,35,35,35]
  coach_dict['phi'] = [23,23,23,23,103]
  coach_dict['wsh'] = [25,25,25,25,25]
  coach_dict['ari'] = [59,59,59,59,107]
  coach_dict['stl'] = [50,50,50,12,12]
  coach_dict['sf'] = [70,70,91,91,91]
  coach_dict['sea'] = [83,83,83,83,83]
  coach_dict['chi'] = [38,38,38,38,102]
  coach_dict['det'] = [71,71,71,71,71]
  coach_dict['gb'] = [58,58,58,58,58]
  coach_dict['atl'] = [67,67,67,67,67]
  coach_dict['min'] = [86,86,86,86,86]
  coach_dict['car'] = [13,13,90,90,90]
  coach_dict['no'] = [42,42,42,50,42]
  coach_dict['tb'] = [75,75,75,100,100]

  return coach_dict[team][4]

def get_coach_ids(cur, plyr_name, week):
  coaches = []
  plyr_team = get_team(cur, plyr_name)
  opp_team = get_opp_team(cur, plyr_team, week)
  plyr_coach = coach(plyr_team) 
  opp_coach = coach(opp_team) 
  coaches.append(plyr_coach)
  coaches.append(opp_coach)
  return coaches

def is_starter(cur, id):
  command = "SELECT is_starter FROM current_starters WHERE plyr_id = '%s' LIMIT 1;" % (id)
  cur.execute(command)
  rows = cur.fetchall()
  if len(rows) == 0:
    return False
  starter = rows[0][0]
  if starter == 1:
    return True
  else:
    return False


def make_predictions(plyrs, week_num):
  db = connect()[0]
  cur = connect()[1]
  predictions = {}
  
  for p in plyrs:
    if p == 'dummy':
      continue
    #gets player name, id, and img url
    disp_name = display_name(p)
    img_name = disp_name.replace('.','')
    pos = plyr_position(cur, disp_name)
    id = player_id(cur, disp_name)
    name = disp_name.replace('-',' ').title()
    img_url = "http://s3-us-west-2.amazonaws.com/nflheadshots/%s-%s.png" % (id, img_name)
    print name, pos, week_num
    
    #gets the names and IDs of the players appearing in the upcoming game
    game_plyr_names = all_players(cur, disp_name, week_num) 
    plyr_ids = []
    if len(game_plyr_names) != 0:
      plyr_ids = convert_names_to_ids(cur, game_plyr_names)
    
    #coach ids and is starter
    coaches = get_coach_ids(cur, disp_name, week_num)
    if is_starter(cur, id):
      coaches.append(99999)  
    feature_arr = plyr_ids + coaches
    
    #predicts points
    pts = 0
    if len(plyr_ids) != 0:
      pts = predict(cur, id, feature_arr)
    plyr_dict = {}
    plyr_dict[name] = (pts, img_url)
    
    if pos == 'PK':
      pos = 'K'
    if pos in predictions:
      predictions[pos].append(plyr_dict)
      predictions[pos].sort(reverse=True, key=lambda elem:elem.values()[0] )
    else:
      predictions[pos] = []
      predictions[pos].append(plyr_dict)
    print "Prediction: ", pts
  cur.close()
  del cur
  db.close()
  del db  
  return predictions
  
  
  