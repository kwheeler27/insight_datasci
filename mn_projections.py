import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB
from mn_predictions import *

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
    starter = is_starter(cur, id)
    if starter:
      coaches.append(99999)  
    feature_arr = plyr_ids + coaches
    
   #predicts points - general heuristics
    pts = 0
    if len(plyr_ids) != 0:
      pts = predict(cur, id, feature_arr)
      if pts == 3:
        if starter:
        
          if (pos == 'RB' or pos == 'QB' or pos == 'WR'):
            if disp_name == 'arian-foster' or disp_name == 'marshawn-lynch' or disp_name == 'lesean-mccoy':
              pts = 8.8
            else:
              pts = 6.7
          elif (pos == 'TE'):
            if disp_name == 'jimmy-graham' or disp_name == 'jason-witten':
              pts = 8
            else:
              pts = 5
          elif (pos == 'PK'):
            pts = 6.5
        else:
          if pos == 'RB' or pos == 'WR':
            pts = 2
          else:
            pts = 1
    
    #gets weights
    
    home_team = get_team(cur, disp_name)
    opp_team = get_opp_team(cur, home_team, week_num)
    off_weight = offense_weight(home_team, pos)
    def_weight = defense_weight(opp_team, pos)
    pts = pts * off_weight * def_weight
    
    pts = round(pts,1)
    '''
    plyr_data = [id, disp_name, pos, pts, week_num]
    predictions.append(plyr_data)
    '''    
    predictions.append(pts)
    
  cur.close()
  db.close()

  return predictions
  
  
  