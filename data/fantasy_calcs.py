import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from mn_projections import *
from helpers import *

"""
This script is used to calculate the fantasy points for all plyrs. 
It gets all offensive players in the DB and then calcs their predicted points scored.
The results are stored in a .csv file
"""
def get_plyr_names(cur):
  arr = []
  command = "SELECT DISTINCT(name), position FROM players;"
  cur.execute(command)
  rows = cur.fetchall()
  for r in rows:
    name, pos = r[0], r[1]  
    if pos == 'WR' or pos == 'PK' or pos == 'QB' or pos == 'RB' or pos == 'TE':  
      arr.append(r[0])
  return arr

def get_names(cur, plyr_ids):
  arr = []
  for id in plyr_ids:
    print id
    command = "SELECT DISTINCT(name) FROM players WHERE plyr_id = '%s';" % (id)
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
  ndarr = np.empty([0,5])
  all_predictions = []
  for w in range(1,19):
    my_proj = make_projections(plyr_names, w)
    all_predictions += my_proj
  ndarr = np.array(all_predictions)

  data = {"plyr_id": ndarr[:,0], "name": ndarr[:,1], "position": ndarr[:,2], "points": ndarr[:,3], "week": ndarr[:,4]}
  valid = pd.DataFrame(data)
  valid.to_csv('fantasy_full_season.csv')
 
 
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()