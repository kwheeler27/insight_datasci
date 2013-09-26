import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB
from predictions import *

def make_projections(plyrs, week_num):
  db = connect()[0]
  cur = connect()[1]
  predictions = []
  
  for p in plyrs:
    if p == 'dummy':
      predictions.append(0)
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
    predictions.append(pts)
    
  cur.close()
  del cur
  db.close()
  del db  
  return predictions
  
  
  