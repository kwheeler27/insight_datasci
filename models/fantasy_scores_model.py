import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from helpers import *

"""
This script creates a table in my MySQL db containing data on each player's fantasy scores
""" 
def main():
  infile = "./fantasy_scores.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='fantasy_scores', if_exists='replace', flavor='mysql')
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()