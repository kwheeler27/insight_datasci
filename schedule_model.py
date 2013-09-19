import requests
import re
import csv
from bs4 import BeautifulSoup
import sys
import MySQLdb as mdb
import pandas as pd
import numpy as np
from pandas.io import sql

#connect to MySQL
def connect():
  #db = mdb.connect(host='localhost', user='root', local_infile = 1) # used if loading from local csv)
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root', passwd='r')
  db.autocommit(True)
  return db, db.cursor()
  
def is_team_row(c):
  return c == 'oddrow' or c == 'evenrow'

def write_sched_csv():
  wfile = open("schedules.csv", "wb")
  field_names = ['id', 'home','away', 'week']
  writer = csv.writer(wfile)
  writer.writerow(field_names)
  count = 1
  teams = ['buf/buffalo-bills', 'mia/miami-dolphins', 'ne/new-england-patriots', 'nyj/new-york-jets', 'den/denver-broncos', 'kc/kansas-city-chiefs', 'oak/oakland-raiders', 'sd/san-diego-chargers', 'bal/baltimore-ravens', 'cin/cincinnati-bengals', 'cle/cleveland-browns', 'pit/pittsburgh-steelers', 'hou/houston-texans', 'ind/indianapolis-colts', 'jac/jacksonville-jaguars', 'ten/tennessee-titans', 'dal/dallas-cowboys', 'nyg/new-york-giants', 'phi/philadelphia-eagles', 'wsh/washington-redskins', 'ari/arizona-cardinals', 'stl/st-louis-rams', 'sf/san-francisco-49ers', 'sea/seattle-seahawks', 'chi/chicago-bears', 'det/detroit-lions', 'gb/green-bay-packers', 'min/minnesota-vikings', 'atl/atlanta-falcons', 'car/carolina-panthers', 'no/new-orleans-saints', 'tb/tampa-bay-buccaneers'] 
  for t in teams:
    team_abbr = t[:3]
    if t[2] == '/':
      team_abbr = t[:2] 
    team_url = "http://espn.go.com/nfl/team/_/name/%s" % (t)
    team_sched = requests.get(team_url)
    soup = BeautifulSoup(team_sched.content)
    table = soup.find('table', class_="tablehead")
    for row in table.find_all('tr', class_=is_team_row):
      cols = row.find_all('td')
      week = int(cols[0].text.encode('ascii','ignore'))
      if cols[1].text.encode('ascii','ignore') != 'BYE WEEK':
        opp_col = cols[2].find_all('a')
        href_str = str(opp_col[1])
        opp_team = re.search(r'/name/(\w+)/', href_str)
        data = [count, team_abbr, opp_team.group(1), week]
        writer.writerow(data)
        count += 1
  wfile.close()
  return
  
def main():
  #write_sched_csv()
  
  infile = "./schedules.csv"
  db = connect()[0]
  cur = connect()[1]
  cur.execute("USE fantasy_lineups;")
  df = pd.read_csv(infile)
  sql.write_frame(df, con=db, name='schedules', if_exists='replace', flavor='mysql')
   
  cur.close()
  db.close()
  
if __name__ == '__main__':
  main()