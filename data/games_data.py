import requests
import json
import re
import time
import csv
import MySQLdb as mdb
from bs4 import BeautifulSoup
from helpers import *

"""
This script scrapes all of the game ids for each player in the DB and stores it in a .csv file.
"""
def main():
  rfile = open("players.csv", "rb")
  reader = csv.DictReader(rfile)
  wfile = open("games-data4.csv", "wb")
  field_names = ['count', 'game_id','plyr_id','name']
  writer = csv.writer(wfile)
  writer.writerow(field_names)

  count = 1
  pcount = 1
  for plyr in reader:
    id = int(plyr['ID'])
    name = plyr['Display Name']
    for year in range(2013,2014):
      gamelog_url = "http://espn.go.com/nfl/player/gamelog/_/id/%d/year/%d/%s" % (id, year, name)
      gamelog_res = requests.get(gamelog_url)
      soup = BeautifulSoup(gamelog_res.content)
      week = 1
      for tr in soup.find_all('tr', class_=is_game_row):
        if week == 2:   
          for child in tr.find_all(href=re.compile('/nfl/boxscore')):
            href_str = str(child)
            game_id = re.search(r'\?gameId=(\d+)', href_str)
            if game_id:
              data = [count, int(game_id.group(1)), id, name]
              writer.writerow(data)
              count += 1
        week += 1
    pcount += 1
  rfile.close()
  wfile.close()
  
if __name__ == '__main__':
  main()