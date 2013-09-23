import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from mn_projections import *


#connect to MySQL
def connect():
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root', passwd='r')
  db.autocommit(True)
  return db, db.cursor()

def get_plyr_ids(cur):
  arr = []
  command = "SELECT plyr_id FROM actual_fantasy_pts WHERE week = '2';"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    if r[0] < 20000:
      arr.append(r[0])
  return arr
  
def get_actual_pts(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    command = "SELECT tot_pts FROM actual_fantasy_pts WHERE week = '2' AND plyr_id = '%s';" % (id)
    cur.execute(command)
    rows = cur.fetchall()
    pts = rows[0][0]
    arr.append(pts)
  return arr
  
def get_proj_pts(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    command = "SELECT proj_pts FROM espn_projections WHERE week = '2' AND plyr_id = '%s';" % (id)
    cur.execute(command)
    rows = cur.fetchall()
    #print rows
    if len(rows) == 0:
      arr.append(0)
    else:
      pts = rows[0][0]
      arr.append(pts)
  return arr
  
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
  db = connect()[0]
  cur = connect()[1]
  print "GETTING IDS..."
  plyr_ids = get_plyr_ids(cur)
  print "GETTING ACT PTS..."
  actual_pts = get_actual_pts(cur, plyr_ids)
  print "GETTING ESPN PROJ..."
  espn_proj = get_proj_pts(cur, plyr_ids)
  print "GETTING MY PROJ..."
  plyr_names = get_names(cur, plyr_ids)
  print "NUM PLYRS: ", len(plyr_names), len(plyr_ids), len(actual_pts), len(espn_proj), 
  my_proj = make_projections(plyr_names, 1)
  arr = [plyr_ids, actual_pts, espn_proj, my_proj]
  data = {'plyr_ids': plyr_ids, 'actual_pts': actual_pts, 'espn_proj': espn_proj, 'my_proj': my_proj}
  print data
  
  valid = pd.DataFrame(data)
  valid.to_csv('validation_week2_mn2.csv')
 
 
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()