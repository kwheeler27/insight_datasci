import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB, MultinomialNB

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
    
#sets X[game_id][plyr_id] = 1 if plyr/coach is in plyrs_in_game
def update_training_matrix(cur, plyrs_in_game, game, X):
  if len(X.values) == 0:
    return
  for p in plyrs_in_game:
    if p in X.ix[game]:
      if p == 99999:
        X.ix[game][p] = 5  
      elif p >= 1 and p <= 120:
        X.ix[game][p] = 4  
      elif is_starter(cur, p):
        X.ix[game][p] = 3
      else:
        X.ix[game][p] = 1
  return

#populates an empty training matrix, X    
def populate_training_set(cur, X, games, plyr_id):
  for g in games:
    plyrs = plyrs_in_game(cur, g, plyr_id) #np.arr - list of players who played in given game (incls coaches/starter)
    update_training_matrix(cur, plyrs, g, X)
  return

def discretize(arr):
  result = []
  for i in arr:
    if i <= 5.0:
      result.append(0)
    elif i > 5.0 and i <= 10.0:
      result.append(1)
    elif i > 10.0 and i <= 15.0:
      result.append(2)
    elif i > 15.0 and i <= 20.0:
      result.append(3)
    elif i > 20.0 and i <= 25.0:
      result.append(4)
    else:
      result.append(5)
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

def weights(games):
  arr = []
  for elem in games:
    if elem < 300909018:
      arr.append(1)
    elif elem >= 300909018 and elem < 310908009:
      arr.append(2)
    elif elem >= 310908009 and elem < 320905019:
      arr.append(3)
    elif elem >= 320905019 and elem < 330905007:
      arr.append(5)
    else:
      arr.append(7)
  return np.array(arr)

def defense_weight(team, pos):
  
  def_dict = {}
  def_dict['buf'] = [2,6]
  def_dict['mia'] = [6,2]
  def_dict['ne'] = [3,5]
  def_dict['nyj'] = [1,3]
  def_dict['den'] = [3,1]
  def_dict['kc'] = [2,3]
  def_dict['oak'] = [2,3]
  def_dict['sd'] = [6,2]
  def_dict['bal'] = [5,3]
  def_dict['cin'] = [2,1]
  def_dict['cle'] = [4,2]
  def_dict['pit'] = [1,2]
  def_dict['hou'] = [1,2]
  def_dict['ind'] = [4,6]
  def_dict['jac'] = [2,6]
  def_dict['ten'] = [4,6]
  def_dict['dal'] = [5,4]
  def_dict['nyg'] = [5,5]
  def_dict['phi'] = [5,6]
  def_dict['wsh'] = [6,5]
  def_dict['ari'] = [3,4]
  def_dict['stl'] = [5,1]
  def_dict['sf'] = [1,3]
  def_dict['sea'] = [1,4]
  def_dict['chi'] = [3,1]
  def_dict['det'] = [3,4]
  def_dict['gb'] = [5,5]
  def_dict['atl'] = [6,4]
  def_dict['min'] = [6,5]
  def_dict['car'] = [4,5]
  def_dict['no'] = [4,6]
  def_dict['tb'] = [6,1]
  result = 1
  if pos == 'WR' or pos == 'QB' or pos == 'TE':
    rank = def_dict[team][0]
    if rank == 1:
      result = 0.87
    if rank == 2:
      result = 0.91
    if rank == 3:
      result = 0.96
    if rank == 4:
      result = 1.04
    if rank == 5:
      result = 1.08
    if rank == 6:
      result = 1.12
  elif pos == 'RB':
    rank = def_dict[team][1]
    if rank == 1:
      result = 0.87
    if rank == 2:
      result = 0.91
    if rank == 3:
      result = 0.96
    if rank == 4:
      result = 1.04
    if rank == 5:
      result = 1.08
    if rank == 6:
      result = 1.12
  else:
    rank = 0.5*(def_dict[team][1] + def_dict[team][0])
    if rank >= 1 and rank < 2:
      result = 0.92
    if rank >= 2 and rank < 3:
      result = 0.95
    if rank >= 3 and rank < 4:
      result = 1
    if rank >= 4 and rank < 5:
      result = 1.05
    else:
      result = 1.08
  return result

def offense_weight(team, pos):
  off_dict = {}
  off_dict['buf'] = [6,1]
  off_dict['mia'] = [4,5]
  off_dict['ne'] = [3,2]
  off_dict['nyj'] = [6,3]
  off_dict['den'] = [1,4]
  off_dict['kc'] = [6,1]
  off_dict['oak'] = [4,3]
  off_dict['sd'] = [4,5]
  off_dict['bal'] = [3,4]
  off_dict['cin'] = [3,4]
  off_dict['cle'] = [5,6]
  off_dict['pit'] = [4,6]
  off_dict['hou'] = [2,1]
  off_dict['ind'] = [3,3]
  off_dict['jac'] = [6,6]
  off_dict['ten'] = [6,4]
  off_dict['dal'] = [2,6]
  off_dict['nyg'] = [2,5]
  off_dict['phi'] = [2,2]
  off_dict['wsh'] = [3,2]
  off_dict['ari'] = [4,6]
  off_dict['stl'] = [2,5]
  off_dict['sf'] = [5,2]
  off_dict['sea'] = [6,1]
  off_dict['chi'] = [5,3]
  off_dict['det'] = [1,5]
  off_dict['gb'] = [1,4]
  off_dict['atl'] = [1,6]
  off_dict['min'] = [6,1]
  off_dict['car'] = [5,2]
  off_dict['no'] = [1,6]
  off_dict['tb'] = [5,3]
  result = 1
  if pos == 'WR' or pos == 'QB' or pos == 'TE':
    rank = off_dict[team][0]
    if rank == 6:
      result = 0.87
    if rank == 5:
      result = 0.93
    if rank == 4:
      result = 0.99
    if rank == 3:
      result = 1.03
    if rank == 2:
      result = 1.07
    if rank == 1:
      result = 1.11
  elif pos == 'RB':
    rank = off_dict[team][1]
    if rank == 6:
      result = 0.87
    if rank == 5:
      result = 0.93
    if rank == 4:
      result = 0.99
    if rank == 3:
      result = 1.03
    if rank == 2:
      result = 1.07
    if rank == 1:
      result = 1.11
  else:
    rank = 0.5*(off_dict[team][1] + off_dict[team][0])
    if rank >= 1 and rank < 2:
      result = 1.08
    if rank >= 2 and rank < 3:
      result = 1.05
    if rank >= 3 and rank < 4:
      result = 1
    if rank >= 4 and rank < 5:
      result = 0.95
    else:
      result = 0.92
  return result


def predict(cur, plyr_id, game_plyrs): 
  #creates training set (called 'X') for plyr
  all_plyrs = all_player_ids(cur) #np.array - all NFL players (and coaches)
  games = games_played_in(cur, plyr_id) #np.array - the games_ids the player played in
  n_cols = all_plyrs.shape[0] #int 
  m_rows = games.shape[0] #int
  w = weights(games)
  zeros = np.zeros((m_rows, n_cols)) #2darr - used to initialize DF
  X = pd.DataFrame(zeros, index=games, columns=all_plyrs) #dataframe
  populate_training_set(cur, X, games, plyr_id)
  print "X: ", X.values
  
  
  #creates vector of known output values
  Y = training_output_vector(cur, games, plyr_id)
  print "(len) Y: ", len(Y), Y
  test_zeros = np.zeros((1, n_cols)) #2darr - used to initialize DF
  test_X = pd.DataFrame(zeros, columns=all_plyrs) #dataframe
  update_training_matrix(cur, game_plyrs, 0, test_X)
  
  #run Bernoulli NB Classifier
  nb_clf = MultinomialNB()
  
  if len(X.values) == 0:
    return 0
  nb_clf.fit(X, Y, sample_weight=w)
  nb_predictions = nb_clf.predict(test_X)
  print "test_X: ", test_X.values
  nb_norm_prob = normalize_probs(nb_clf.predict_proba(test_X)[0])
  avgs = range(3,30,5)
  print "probs: ", nb_norm_prob
  print avgs
  ev = expected_val(nb_norm_prob, avgs) #can also calc dot product
  return round(ev,1)
  
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
    starter = is_starter(cur, id)
    if starter:
      coaches.append(99999)  
    feature_arr = plyr_ids + coaches
    
    #predicts points - general heuristics
    pts = 0
    if len(plyr_ids) != 0:
      pts = predict(cur, id, feature_arr)
      if pts == 3:
        if starter and (pos == 'RB' or pos == 'QB'):
          if disp_name == 'arian-foster' or disp_name == 'marshawn-lynch' or disp_name == 'lesean-mccoy':
            pts = 9
          else:
            pts = 6
        elif starter and (pos == 'WR'):
          pts = 4
        else:
          if pos == 'RB' or pos == 'WR':
            pts = 2
          else:
            pts = 1
      if not starter and pos == 'TE':
        pts = 1
    #gets weights
    '''
    home_team = get_team(cur, disp_name)
    opp_team = get_opp_team(cur, home_team, week_num)
    off_weight = offense_weight(home_team, pos)
    def_weight = defense_weight(opp_team, pos)
    pts = pts * off_weight * def_weight
    '''
    
    plyr_dict = {}
    plyr_dict[name] = (round(pts,1), img_url)
    
    if pos == 'PK':
      pos = 'K'
    if pos in predictions:
      predictions[pos].append(plyr_dict)
      predictions[pos].sort(reverse=True, key=lambda elem:elem.values()[0] )
    else:
      predictions[pos] = []
      predictions[pos].append(plyr_dict)
    print "Prediction: ", pts
    print "MN"
  cur.close()
  del cur
  db.close()
  del db  
  return predictions
  
  
  