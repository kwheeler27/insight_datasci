import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
for helpers import *

"""
This script creates a table having a schema of game_id, plyr_id, tot_pts, and week.
It takes in a .csv file containing the data and stores the fantasy points scored by each player in the given week.
It's used for validation.
"""  
def main():
  field_names = ['plyr_id', 'tot_pts','week']
  infile = "./espn-actual2.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='actual_fantasy_pts', if_exists='replace', flavor='mysql')
   
  cur.close()
  del cur
  db.close()
  del db  
  
if __name__ == '__main__':
  main()