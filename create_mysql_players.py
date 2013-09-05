import sys
import MySQLdb as mdb


#connect to MySQL
def connect():
  #db = mdb.connect(host='localhost', user='root', local_infile = 1) # used if loading from local csv)
  db = mdb.connect(host='localhost', db='insight_db', user='root')
  db.autocommit(True)
  return db, db.cursor()

#Create DB
def create_db(cur):
  statement = "CREATE DATABASE insight_db;"
  cur.execute(statement);
  return

#create players table
def create_players_tbl(cur):
  ########################
  # Create customers table
  ########################
  sql = """CREATE TABLE players
  (
    plyr_id      int       NOT NULL ,
    full_name    char(100) NOT NULL ,
    first_name   char(50)  NULL ,
    last_name    char(50)  NULL ,
    url          char(255) NULL ,
    display_name char(100) NOT NULL ,
    PRIMARY KEY (plyr_id)
  ) ENGINE=InnoDB;"""
  cur.execute(sql)
  return
  
#create games table
def create_games_tbl(cur):
  ########################
  # Create customers table
  ########################
  sql = """CREATE TABLE games
  (
    id            int       NOT NULL AUTO_INCREMENT,
    game_id       int       NOT NULL ,
    player_id     int       NOT NULL ,
    year          int       NULL ,
    rush_yds      int       NULL ,
    rec_yds       int       NULL ,
    pass_yds      int       NULL ,
    r_tds         int       NULL ,
    pass_tds      int       NULL ,
    two_pt        int       NULL ,
    fg0           int       NULL ,
    fg20          int       NULL ,
    fg30          int       NULL ,
    fg40          int       NULL ,
    fg50          int       NULL ,
    pat           int       NULL ,
    fum           int       NULL ,
    intercepts    int       NULL ,
    news          char(255) NULL ,
    PRIMARY KEY (id)
  ) ENGINE=InnoDB;"""
  cur.execute(sql)
  return

#populate player table from csv file
def populate_plyr_tbl(cur, filename):
  sql = """LOAD DATA LOCAL INFILE "%s" INTO TABLE players 
  FIELDS TERMINATED BY ',' 
  IGNORE 1 LINES
  (@var0, @var1, @var2, @var3, @var4, @var5)
  SET 
  plyr_id = @var0,
  full_name = @var1,
  first_name = RTRIM(@var2),
  last_name = RTRIM(@var3),
  url = RTRIM(@var4),
  display_name = REPLACE(@var5,'\r','');""" % (filename)
  print sql
  cur.execute(sql)
  return
  
def main():
  infile = "./players.csv"
  db = connect()[0]
  cur = connect()[1]
  #create_db(cur)
  #cur.execute("USE insight_db;")
  #create_players_tbl(cur)
  #populate_plyr_tbl(cur, infile)
  
  #test
  command = "SELECT * FROM players limit 5;"
  output = cur.execute(command)
  rows = cur.fetchall()
  print rows
   
  cur.close()
  del cur
  db.close()
  del db

  
if __name__ == '__main__':
  main()