import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

def is_team_row(c):
  return c == 'oddrow' or c == 'evenrow'

def remove_duplicates(darr):
  new_arr = []
  #[['plyr_id', 'name', 'position', 'is_starter'],['plyr_id', 'name', 'position', 'is_starter']]
  for i in xrange(darr.shape[0]):
    plyr_id_i = darr[i][0]
    is_starter_i = darr[i][3]   
    unique = True
    for j in range(len(new_arr)):
      plyr_id_j = new_arr[j][0]
      is_starter_j = new_arr[j][3]
      if plyr_id_j == plyr_id_i:
        if is_starter_j == 1 and is_starter_i == 0:
          new_arr[j][3] = 1
        unique = False
    if unique:
      new_arr.append(darr[i])
  return np.array(new_arr)

def main():
  field_names = ['plyr_id', 'name', 'position', 'is_starter']
  count = 887
  teams = ['buf/buffalo-bills', 'mia/miami-dolphins', 'ne/new-england-patriots', 'nyj/new-york-jets', 'den/denver-broncos', 'kc/kansas-city-chiefs', 'oak/oakland-raiders', 'sd/san-diego-chargers', 'bal/baltimore-ravens', 'cin/cincinnati-bengals', 'cle/cleveland-browns', 'pit/pittsburgh-steelers', 'hou/houston-texans', 'ind/indianapolis-colts', 'jac/jacksonville-jaguars', 'ten/tennessee-titans', 'dal/dallas-cowboys', 'nyg/new-york-giants', 'phi/philadelphia-eagles', 'wsh/washington-redskins', 'ari/arizona-cardinals', 'stl/st-louis-rams', 'sf/san-francisco-49ers', 'sea/seattle-seahawks', 'chi/chicago-bears', 'det/detroit-lions', 'gb/green-bay-packers', 'min/minnesota-vikings', 'atl/atlanta-falcons', 'car/carolina-panthers', 'no/new-orleans-saints', 'tb/tampa-bay-buccaneers'] 
  players = []
  for t in teams:
    team = t[:3]
    if t[2] == '/':
      team = t[:2] 
    depthchart_url = "http://espn.go.com/nfl/team/depth/_/name/%s" % (team)
    depthchart_res = requests.get(depthchart_url)
    soup = BeautifulSoup(depthchart_res.content)
    table = soup.find('table', class_="tablehead")
    for row in table.find_all('tr', class_=is_team_row):
      cols = row.find_all('td')
      position = cols[0].text.encode('ascii','ignore')
      for i in range(1,3):
        if i == 1 or (position == 'WR' or position == 'RB' or position == 'TE' or position == 'QB'):
          href = cols[i].find_all('a')
          href_str = str(href)
          plyr_id = re.search(r'/id/(\d+)/([\w.\'-]+-[\w\']+)', href_str)
          if plyr_id:
            data = []
            if i == 1:
              data = [int(plyr_id.group(1)), plyr_id.group(2), position,1]
            else:
              data = [int(plyr_id.group(1)), plyr_id.group(2), position,0]  
            players.append(data)
            count += 1
  
  starter_data = np.array(players)
  uni_starter_data = remove_duplicates(starter_data)
  starter_frame = pd.DataFrame(uni_starter_data, columns=['plyr_id', 'name', 'position', 'is_starter'])
  starter_frame.to_csv('starters_2013.csv')
  
if __name__ == '__main__':
  main()