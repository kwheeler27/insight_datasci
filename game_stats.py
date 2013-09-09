import requests
import re
import time
import csv
from bs4 import BeautifulSoup

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
    sacks = int(cols[3].text.encode('ascii', 'ignore'))
    def_tds = int(cols[7].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, sacks, def_tds, 0])
  elif cat == 'returns':
    def_tds = int(cols[5].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, def_tds, 0])
  elif cat == 'kicking':
    kick_pts = int(cols[5].text.encode('ascii', 'ignore'))
    data.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, kick_pts])
  return data
  
def main():
  '''
  wfile = open("game_stats.csv", "wb")
  field_names = ['count', 'game_id','plyr_id', 'pass_yds', 'pass_tds', 'pass_ints', 'rush_yds', 'rush_tds', 'rec_yds', 'rec_tds', 'fum_lost', 'interceptions', 'sacks', 'def_tds', 'kick_pts']
  writer = csv.writer(wfile)
  writer.writerow(field_names)
  '''
  count = 1
  #teams = ['buf/buffalo-bills', 'mia/miami-dolphins', 'ne/new-england-patriots', 'nyj/new-york-jets', 'den/denver-broncos', 'kc/kansas-city-chiefs', 'oak/oakland-raiders', 'sd/san-diego-chargers', 'bal/baltimore-ravens', 'cin/cincinnati-bengals', 'cle/cleveland-browns', 'pit/pittsburgh-steelers', 'hou/houston-texans', 'ind/indianapolis-colts', 'jac/jacksonville-jaguars', 'ten/tennessee-titans', 'dal/dallas-cowboys', 'nyg/new-york-giants', 'phi/philadelphia-eagles', 'wsh/washington-redskins', 'ari/arizona-cardinals', 'stl/st-louis-rams', 'sf/san-francisco-49ers', 'sea/seattle-seahawks', 'chi/chicago-bears', 'det/detroit-lions', 'gb/green-bay-packers', 'min/minnesota-vikings', 'atl/atlanta-falcons', 'car/carolina-panthers', 'no/new-orleans-saints', 'tb/tampa-bay-buccaneers'] 
  
  games = [330908014]
  for game in games:
    boxscore_url = "http://scores.espn.go.com/nfl/boxscore?gameId=%s" % (game)
    boxscore_res = requests.get(boxscore_url)
    soup = BeautifulSoup(boxscore_res.content)
    stat_tables = soup.find_all('table', class_="mod-data")
    for table in stat_tables:
      hdr = table.find('th').text.encode('ascii', 'ignore')
      stat_category = get_stat_category(hdr)
      print 'stat_category: ', stat_category
      for row in table.find_all('tr', class_=is_stat_row):
        cols = row.find_all('td')
        plyr_data = get_plyr_data(cols, stat_category)
        if stat_category == 'NO MATCH' and len(plyr_data) != 0:
          plyr_data.extend([0,0,0,0,0,0,0,0,0,0,0,0])
        print 'plyr_data: ', plyr_data
        
        
        
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
  wfile.close()
  '''
if __name__ == '__main__':
  main()