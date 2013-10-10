import csv
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql
from helpers import *


def main():  
  infile = "./games-data2.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='matchups', if_exists='replace', flavor='mysql')
   
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()