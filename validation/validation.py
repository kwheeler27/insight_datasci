import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from mn_projections import *
from helpers import *

"""
This script is used to validate my predictions for a given week. 
It retrieves and calculates each player's predictions using my model, 
retrieves ESPN's projections (which are stored on my MySQL db), 
retrieves how many points each player actually scored (also stored in db),
and then writes the data to a csv file for comparison in Excel.
"""

#returns a list of players who scored a fantasy point for week 2 of the 2013 season
def get_plyr_ids(cur):
  arr = []
  command = "SELECT plyr_id FROM actual_fantasy_pts WHERE week = '2';"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    if r[0] < 20000:
      arr.append(r[0])
  return arr

#returns a list of the points each player scored for week 2  
def get_actual_pts(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    command = "SELECT tot_pts FROM actual_fantasy_pts WHERE week = '2' AND plyr_id = '%s';" % (id)
    cur.execute(command)
    rows = cur.fetchall()
    pts = rows[0][0]
    arr.append(pts)
  return arr
 
#returns a list of ESPN's projections for each player for week 2  
def get_proj_pts(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    command = "SELECT proj_pts FROM espn_projections WHERE week = '2' AND plyr_id = '%s';" % (id)
    cur.execute(command)
    rows = cur.fetchall()
    if len(rows) == 0:
      arr.append(0)
    else:
      pts = rows[0][0]
      arr.append(pts)
  return arr

#returns a list of player names given their IDs
def get_names(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    print id
    command = "SELECT name FROM players WHERE plyr_id = '%s';" % (id)
    cur.execute(command)
    rows = cur.fetchall()
    if len(rows) == 0:
      arr.append('dummy')
    else:
      name = rows[0][0]
      arr.append(name)
  return arr

def main():
  db = connect()[0] #connects to DB
  cur = connect()[1]
  print "GETTING IDS..."
  plyr_ids = get_plyr_ids(cur) #gets player IDs
  print "GETTING ACT PTS..."
  actual_pts = get_actual_pts(cur, plyr_ids) #gets num pts each player scored
  print "GETTING ESPN PROJ..."
  espn_proj = get_proj_pts(cur, plyr_ids) #gets ESPN's projections
  print "GETTING MY PROJ..."
  plyr_names = get_names(cur, plyr_ids) #converts IDs to names
  print "NUM PLYRS: ", len(plyr_names), len(plyr_ids), len(actual_pts), len(espn_proj), 
  my_proj = make_projections(plyr_names, 1) #calculates each player's predicted score using my algorithm
  arr = [plyr_ids, actual_pts, espn_proj, my_proj]
  data = {'plyr_ids': plyr_ids, 'actual_pts': actual_pts, 'espn_proj': espn_proj, 'my_proj': my_proj}
  
  #writes data to csv file and closes db access
  valid = pd.DataFrame(data)
  valid.to_csv('validation_week2_mn2.csv')
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()