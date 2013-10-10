import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from helpers import *
 
"""
This script loads and stores coaching data into MySQL db.
"""  
def main():
  field_names = ['game_id','coach_id', 'team', 'is_home', 'year']
  infile = "./coach_data.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='coaches', if_exists='replace', flavor='mysql')
   
  cur.close()
  del cur
  db.close()
  del db  
  
if __name__ == '__main__':
  main()