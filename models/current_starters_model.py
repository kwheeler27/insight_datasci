import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from helpers import *

"""
This script stores all of the current starting players in the league.
"""  
def main():
  field_names = ['plyr_id', 'name', 'position', 'is_starter']
  infile = "./starters_2013.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='current_starters', if_exists='replace', flavor='mysql')
   
  cur.close()
  del cur
  db.close()
  del db  
  
if __name__ == '__main__':
  main()