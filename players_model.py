import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql


#Create DB
def create_db(cur):
  statement = "CREATE DATABASE fantasy_lineups;"
  cur.execute(statement);
  return

#create players table
def create_players_tbl(cur):
  ########################
  # Create customers table
  ########################
  sql = """CREATE TABLE players
  (
    plyr_id       int       NOT NULL ,
    display_name  char(100) NOT NULL ,
    position      char(10)  NULL ,
    team          char(10)  NULL ,
    PRIMARY KEY (plyr_id)
  ) ENGINE=InnoDB;"""
  cur.execute(sql)
  return

#populate player table from csv file
def populate_plyr_tbl(cur, filename):
  sql = """LOAD DATA LOCAL INFILE "%s" INTO TABLE players 
  FIELDS TERMINATED BY ',' 
  IGNORE 1 LINES
  (@var0, @var1, @var2, @var3)
  SET 
  plyr_id = @var0,
  display_name = @var1,
  position = @var2,
  team = @var3;""" % (filename)
  print sql
  cur.execute(sql)
  return
  
def main():
  infile = "./all_players.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='players', if_exists='replace', flavor='mysql')
   
  cur.close()
  del cur
  db.close()
  del db  
  
if __name__ == '__main__':
  main()