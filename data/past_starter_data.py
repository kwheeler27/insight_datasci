import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import string

"""
This script scrapes past starter info for all players.
"""
def is_stat_row(c):
  return (c == 'odd' or c == 'even')

def get_stat_category(str):
  if re.search(r'[\w.\s]+(Passing)', str):
    return 'passing'
  elif re.search(r'[\w.\s]+(Rushing)', str):
    return 'rushing'
  elif re.search(r'[\w.\s]+(Receiving)', str):
    return 'receiving'
  elif re.search(r'[\w.\s]+(Fumbles)', str):
    return 'fumbles'
  elif re.search(r'[\w.\s]+(Interceptions)', str):
    return 'interceptions'
  elif re.search(r'[\w.\s]+(Defensive)', str):
    return 'defensive'
  elif re.search(r'[\w.\s]+(Returns)', str):
    return 'returns'
  elif re.search(r'[\w.\s]+(Kicking)', str):
    return 'kicking'
  elif re.search(r'[\w.\s]+(Tackles)', str):
    return 'defensive'
  else:
    return 'NO MATCH'

def get_plyr_data(cols, cat, row_num):
  data = []
  if len(cols) == 0:
    return []
  href = cols[0].find_all('a')
  href_str = str(href)
  plyr_id = re.search(r'/id/(\d+)/([\w.\'-]+-[\w\']+)', href_str)
  if plyr_id:
    data.append(plyr_id.group(1))
    data.append(plyr_id.group(2))
    
    if cat == 'passing':
      if row_num == 1:
        data.append(1)
      else:
        data.append(0)
    elif cat == 'rushing':
      if row_num == 1:
        data.append(1)
      else:
        data.append(0)
    elif cat == 'receiving':
      if row_num < 5:
        data.append(1)
      else:
        data.append(0)
    elif cat == 'kicking':
      if row_num == 1:
        data.append(1)
      else:
        data.append(0)
    else:
      data.append(0)
  return data

def remove_duplicates(darr):
  new_arr = []
  #[['game_id','plyr_id', 'name', 'is_starter'],['game_id','plyr_id', 'name', 'is_starter']]
  for i in xrange(darr.shape[0]):
    game_id_i = darr[i][0]
    plyr_id_i = darr[i][1]
    is_starter_i = darr[i][3]   
    unique = True
    for j in range(len(new_arr)):
      game_id_j = new_arr[j][0]
      plyr_id_j = new_arr[j][1]
      is_starter_j = new_arr[j][3]
      if game_id_j == game_id_i and plyr_id_j == plyr_id_i:
        if is_starter_j == 1 and is_starter_i == 0:
          new_arr[j][3] = 1
        unique = False
    if unique:
      new_arr.append(darr[i])
  return np.array(new_arr)

def main():
  #read in game_ids
  games_data = pd.read_csv('games-data.csv')
  all_games = np.array(games_data['game_id'])
  uni_game_ids = np.unique(all_games)
  
  count = 1
  games = [330908014]
  game_data = []
  print "GAME IDS READ. GETTING GAME DATA..."
  for game in uni_game_ids:
    print count, game
    count += 1
    boxscore_url = "http://scores.espn.go.com/nfl/boxscore?gameId=%s" % (game)
    boxscore_res = requests.get(boxscore_url)
    soup = BeautifulSoup(boxscore_res.content)
    stat_tables = soup.find_all('table', class_="mod-data")
    plyrs = []
    for table in stat_tables:
      hdr = table.find('th').text.encode('ascii', 'ignore')
      stat_category = get_stat_category(hdr)
      row_num = 1
      for row in table.find_all('tr', class_=is_stat_row):
        cols = row.find_all('td')
        plyr_data = get_plyr_data(cols, stat_category, row_num)
        #if stat_category == 'NO MATCH' and len(plyr_data) != 0:
         # plyr_data.extend([0])
               
        if len(plyr_data) != 0:
          plyr_data.insert(0, game)
          game_data.append(plyr_data)
  
  starter_data = np.array(game_data)
  #print "BEFORE: ", starter_data.shape[0]
  uni_starter_data = remove_duplicates(starter_data)
  #print "AFTER: ", uni_starter_data.shape[0]
  starter_frame = pd.DataFrame(uni_starter_data, columns=['game_id','plyr_id', 'name', 'is_starter'])
  starter_frame.to_csv('starter_data.csv')
  
if __name__ == '__main__':
  main()