import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import string

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

def get_plyr_data(cols, cat):
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
    pass_yds = int(cols[2].text.encode('ascii', 'ignore'))
    pass_tds = int(cols[4].text.encode('ascii', 'ignore'))
    pass_ints = int(cols[5].text.encode('ascii', 'ignore'))
    data.extend([pass_yds, pass_tds, pass_ints, 0,0,0,0,0,0,0,0,0])
  elif cat == 'rushing':
    rush_yds = int(cols[2].text.encode('ascii', 'ignore'))
    rush_tds = int(cols[4].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, rush_yds, rush_tds, 0, 0, 0, 0, 0, 0, 0])
  elif cat == 'receiving':
    rec_yds = int(cols[2].text.encode('ascii', 'ignore'))
    rec_tds = int(cols[4].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, rec_yds, rec_tds, 0, 0, 0, 0, 0])
  elif cat == 'fumbles':
    fum_lost = int(cols[2].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, fum_lost, 0, 0, 0, 0])
  elif cat == 'interceptions':
    ints = int(cols[1].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, ints, 0, 0, 0])
  elif cat == 'defensive':
    sacks = float(cols[3].text.encode('ascii', 'ignore'))
    def_tds = int(cols[7].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, sacks, def_tds, 0])
  elif cat == 'returns':
    def_tds = 0
    if len(cols) < 6:
      def_tds = int(cols[4].text.encode('ascii', 'ignore'))
      if def_tds > 2:
        def_tds = 0
    else:
      def_tds = int(cols[5].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, def_tds, 0])
  elif cat == 'kicking':
    kick_pts = 0
    if len(cols) < 6:
      kick_pts = int(cols[4].text.encode('ascii', 'ignore'))
    else:
      kick_pts = int(cols[5].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, kick_pts])
  return data

def fantasy_pts(arr):
  pts = 0
  pts += float(arr[0]) / 25.0  #pass yds
  pts += float(arr[1]) * 4     #pass tds
  pts -= float(arr[2])         #pass ints
  pts += float(arr[3]) / 10.0  #rush yds
  pts += float(arr[4]) * 6     #rush tds
  pts += float(arr[5]) / 10.0  #rec yds
  pts += float(arr[6]) * 6     #rec tds
  pts -= float(arr[7]) * 2     #'fum_lost'
  pts += float(arr[8]) * 2     #'interceptions', 
  pts += float(arr[9])         #'sacks'
  pts += float(arr[10]) * 6     #'def_tds'
  pts += float(arr[11])        #'kick_pts'
  return pts

def calc_scores(arr2d):
  print "CALCULATING SCORES..."
  scores = [['game_id','plyr_id', 'name', 'score']]
  for row in arr2d:
    arr = [row[0], row[1], row[2]]
    if arr[1] != 0:
      arr.append(fantasy_pts(row[3:]))
      print arr
      scores.append(arr)
  plyr_pts = np.array(scores)
  return plyr_pts

def consolidate_scores(arr2d):
  print "CONSOLIDATING SCORES..."
  new_scores = []
  col1 = arr2d[1:,0]
  col2 = arr2d[1:,1]
  col3 = arr2d[1:,2]
  col4 = arr2d[1:,3]
  new_arr2d = arr2d[1:,:]
  col_temp = []
  for i in xrange(col1.shape[0]):
    col_temp.append(string.join(col1[i], col2[i]))
  uni_col_temp = np.unique(col_temp)
  
  result = []
  for i in xrange(uni_col_temp.shape[0]):
    uni_id = uni_col_temp[i]
    tot_pts = 0
    elems = []
    for j in xrange(col1.shape[0]):
      game = col1[j]
      plyr = col2[j]
      name = col3[j]
      test = string.join(game, plyr)
      if test == uni_id:
        if len(elems) == 0:
          elems.append(game)
          elems.append(plyr)
          elems.append(name)
        tot_pts += float(col4[j])
    elems.append(tot_pts)
    result.append(elems)
  return np.array(result) 
  
def main():
  #read in game_ids
  games_data = pd.read_csv('games-data.csv')
  all_games = np.array(games_data['game_id'])
  uni_game_ids = np.unique(all_games)
  
  #open write file, write field names
  #wfile = open("fantasy_scores.csv", "wb")
  field_names = ['game_id','plyr_id', 'name', 'pass_yds', 'pass_tds', 'pass_ints', 'rush_yds', 'rush_tds', 'rec_yds', 'rec_tds', 'fum_lost', 'interceptions', 'sacks', 'def_tds', 'kick_pts']
  #writer = csv.writer(wfile)
  #writer.writerow(field_names)
  count = 1
  #teams = ['buf/buffalo-bills', 'mia/miami-dolphins', 'ne/new-england-patriots', 'nyj/new-york-jets', 'den/denver-broncos', 'kc/kansas-city-chiefs', 'oak/oakland-raiders', 'sd/san-diego-chargers', 'bal/baltimore-ravens', 'cin/cincinnati-bengals', 'cle/cleveland-browns', 'pit/pittsburgh-steelers', 'hou/houston-texans', 'ind/indianapolis-colts', 'jac/jacksonville-jaguars', 'ten/tennessee-titans', 'dal/dallas-cowboys', 'nyg/new-york-giants', 'phi/philadelphia-eagles', 'wsh/washington-redskins', 'ari/arizona-cardinals', 'stl/st-louis-rams', 'sf/san-francisco-49ers', 'sea/seattle-seahawks', 'chi/chicago-bears', 'det/detroit-lions', 'gb/green-bay-packers', 'min/minnesota-vikings', 'atl/atlanta-falcons', 'car/carolina-panthers', 'no/new-orleans-saints', 'tb/tampa-bay-buccaneers'] 
  
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
    for table in stat_tables:
      hdr = table.find('th').text.encode('ascii', 'ignore')
      stat_category = get_stat_category(hdr)
      for row in table.find_all('tr', class_=is_stat_row):
        cols = row.find_all('td')
        plyr_data = get_plyr_data(cols, stat_category)
        if stat_category == 'NO MATCH' and len(plyr_data) != 0:
          plyr_data.extend([0,0,0,0,0,0,0,0,0,0,0,0])       
        if len(plyr_data) != 0:
          plyr_data.insert(0, game)
          game_data.append(plyr_data)
  game_stats = np.array(game_data)
  fantasy_scores = calc_scores(game_stats)
  consolidated_scores = consolidate_scores(fantasy_scores)
  fantasy_frame = pd.DataFrame(consolidated_scores, columns=['game_id','plyr_id', 'name', 'fntsy_pts'])
  fantasy_frame.to_csv('fantasy_scores.csv')
  #print consolidated_scores
     
        
  '''
    for row in table.find_all('tr', class_=is_team_row):
      cols = row.find_all('td')
      position = cols[0].text.encode('ascii','ignore')
      for i in range(1,3):
        if i == 1 or (position == 'WR' or position == 'RB' or position == 'TE'):
          href = cols[i].find_all('a')
          href_str = str(href)
          plyr_id = re.search(r'/id/(\d+)/([\w.\'-]+-[\w\']+)', href_str)
          if plyr_id:
            data = [count, team, int(plyr_id.group(1)), plyr_id.group(2), position]
            print data
            writer.writerow(data)
            count += 1
  '''
  #wfile.close()
  
if __name__ == '__main__':
  main()