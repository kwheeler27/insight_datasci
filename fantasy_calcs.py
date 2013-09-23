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

def get_plyr_names(cur):
  arr = []
  command = "SELECT DISTINCT(name) FROM players;"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    if r[0] < 20000:
      arr.append(r[0])
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
  print "GETTING NAMES..."
  plyr_names = get_plyr_names(cur)
  
  all_predictions = []
  for w in range(1,19):
    my_proj = make_projections(plyr_names, w)
    #plyr_data = [id, disp_name, pos, pts, week_num]
    
    all_predictions += my_proj
  data = {"plyr_id": all_predictions[:,0], "name": all_predictions[:,1], "position": all_predictions[:,2], "points": all_predictions[:,3], "week": all_predictions[:,4]}
  valid = pd.DataFrame(data)
  valid.to_csv('fantasy_full_season.csv')
 
 
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()