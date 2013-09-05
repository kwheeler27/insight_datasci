import requests
import json
import re
import time
import csv
import MySQLdb as mdb
from bs4 import BeautifulSoup

def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  rfile = open("players.csv", "rb")
  #field_names = ['ID','Full Name','First Name','Last Name','Player URL','Display Name']
  reader = csv.DictReader(rfile)
  wfile = open("test.csv", "wb")
  field_names = ['count', 'game_id','plyr_id']
  writer = csv.writer(wfile)
  writer.writerow(field_names)

  count = 1
  pcount = 1
  for plyr in reader:
    id = int(plyr['ID'])
    name = plyr['Display Name']
    for year in range(2009,2013):
      gamelog_url = "http://espn.go.com/nfl/player/gamelog/_/id/%d/year/%d/%s" % (id, year, name)
      gamelog_res = requests.get(gamelog_url)
      soup = BeautifulSoup(gamelog_res.content)
      for tr in soup.find_all('tr', class_=is_game_row):
        #print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
        for child in tr.find_all(href=re.compile('/nfl/boxscore')):
          href_str = str(child)
          game_id = re.search(r'\?gameId=(\d+)', href_str)
          if game_id:
            #print game_id.group(1)
            data = [count, int(game_id.group(1)), id]
            writer.writerow(data)
            count += 1
        #print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print pcount
    pcount += 1
    
    
  rfile.close()
  wfile.close()
if __name__ == '__main__':
  main()