import MySQLdb as mdb
import numpy as np
import math
import numpy as np
import pandas as pd


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
  plyr_arr = ['p1', 'p2', 'p3','p4','p5','p6', 'p7', 'p8','p9','p10','p11', 'p12']#, 'p13','p14','p15','p16', 'p17', 'p18','p19','p20']
  names = []
  for p in plyr_arr:
    val = form[p]
    if len(val) != 0:
      names.append(form[p].encode('ascii', 'ignore'))
  return names

#returns the team abbreviation that a given player plays for
def plyr_data(cur, plyr, week):
  command = "SELECT position, plyr_id, points FROM all_predictions WHERE name = '%s' AND week = '%s';" % (mdb.escape_string(plyr), week)
  cur.execute(command)
  rows = cur.fetchall()
  return rows[0][0], rows[0][1], rows[0][2]

def weekly_rank(cur, pos, id, week):
  command = "SELECT plyr_id FROM all_predictions WHERE week = '%s' and position = '%s' ORDER BY points DESC;" % (week, pos)
  cur.execute(command)
  rows = cur.fetchall()
  rankings = []
  for r in rows:
    rankings.append(r[0])
  if id in rankings:
    return rankings.index(id) + 1
  else:
    return 'NA'


def calc_predictions(plyrs, week_num):
  db = connect()[0]
  cur = connect()[1]
  predictions = {}
  for p in plyrs:
    if p == 'dummy':
      continue
    #gets player name, id, and img url
    disp_name = display_name(p)
    img_name = disp_name.replace('.','')
    pos, id, pts = plyr_data(cur, disp_name, week_num)
    print "name: ", disp_name, "pos: ", pos, "id: ", id, "pts: ", pts
    name = disp_name.replace('-',' ').title()
    img_url = "http://s3-us-west-2.amazonaws.com/nflheadshots/%s-%s.png" % (id, img_name)
    
    rank = weekly_rank(cur, pos, id, week_num)
    
    
    
    plyr_dict = {}
    plyr_dict[name] = (round(pts,1), img_url, rank) 
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
  
  
  