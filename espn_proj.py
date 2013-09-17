import requests
import json
import re
import time
import csv
import MySQLdb as mdb
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  wfile = open("espn-proj.csv", "wb")
  field_names = ['plyr_id', 'proj_pts','week']
  writer = csv.writer(wfile)
  writer.writerow(field_names)
  for w in range(1,3):
    for pg in range(0, 320, 40): 
      proj_url = "http://games.espn.go.com/ffl/tools/projections?&scoringPeriodId=%s&seasonId=2013&startIndex=%s" % (w, pg)
      proj_res = requests.get(proj_url)
      soup = BeautifulSoup(proj_res.content)
      for tr in soup.find_all('tr', class_="pncPlayerRow"):
        id_match = re.search(r'plyr(\d+)',tr['id'])
        id = int(id_match.group(1))
        td = tr.find('td', class_="playertableStat appliedPoints sortedCell")
        projpts = td.contents[0].encode('ascii', 'ignore')
        if projpts == '--':
          projpts = 0
        data = [id, projpts, w]
        print data
        writer.writerow(data)
  wfile.close()
if __name__ == '__main__':
  main()