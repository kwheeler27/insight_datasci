import csv
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from helpers import *
  
"""
This script creates a table containing information about past starters. 
It contains the game IDs, player IDs, player name, and if that player was a starter.
"""  
def main():
  field_names = ['game_id','plyr_id','name','is_starter']
  infile = "./past_starter_data.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='past_starters', if_exists='replace', flavor='mysql')
   
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()