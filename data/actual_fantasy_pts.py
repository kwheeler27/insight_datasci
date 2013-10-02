import requests
import json
import re
import time
import csv
import MySQLdb as mdb
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from helpers import *

"""
This script scrapes and stores the fantasy points achieved by each player for the 2013 season.
The data is stored in a .csv file.
"""
def main():
  #open .csv file to store data and writes col names
  wfile = open("espn-actual2.csv", "wb")
  field_names = ['game_id', 'plyr_id', 'tot_pts','week']
  writer = csv.writer(wfile)
  writer.writerow(field_names)
  
  #for each week in the 2013 season, the player id, game id, and points scored are scraped and stored in the .csv file
  for w in range(1,3):
    for pg in range(0, 300, 50): 
      pts_url = "http://games.espn.go.com/ffl/leaders?&scoringPeriodId=%s&seasonId=2013&startIndex=%s" % (w, pg)
      pts_res = requests.get(pts_url)
      soup = BeautifulSoup(pts_res.content)
      for tr in soup.find_all('tr', class_="pncPlayerRow"):
        id_match = re.search(r'plyr(\d+)',tr['id'])
        id = int(id_match.group(1))
        td_pts = tr.find('td', class_="playertableStat appliedPoints appliedPointsProGameFinal")
        projpts = td_pts.contents[0].encode('ascii', 'ignore')
        td_game = tr.find('td', class_="gameStatusDiv")
        href = td_game.find('a')
        href_str = str(href)
        game_match = re.search(r'gameId=(\d+)', href_str)
        game_id = game_match.group(1)
        if projpts == '--':
          projpts = 0
        data = [game_id, id, projpts, w]
        writer.writerow(data)
  wfile.close()
if __name__ == '__main__':
  main()