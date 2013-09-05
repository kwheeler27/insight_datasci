import requests
import re
import time
import csv
from bs4 import BeautifulSoup

def is_team_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  wfile = open("off-rosters.csv", "wb")
  field_names = ['count', 'team','plyr_id', 'name', 'position']
  writer = csv.writer(wfile)
  writer.writerow(field_names)

  count = 887
  teams = ['buf/buffalo-bills', 'mia/miami-dolphins', 'ne/new-england-patriots', 'nyj/new-york-jets', 'den/denver-broncos', 'kc/kansas-city-chiefs', 'oak/oakland-raiders', 'sd/san-diego-chargers', 'bal/baltimore-ravens', 'cin/cincinnati-bengals', 'cle/cleveland-browns', 'pit/pittsburgh-steelers', 'hou/houston-texans', 'ind/indianapolis-colts', 'jac/jacksonville-jaguars', 'ten/tennessee-titans', 'dal/dallas-cowboys', 'nyg/new-york-giants', 'phi/philadelphia-eagles', 'wsh/washington-redskins', 'ari/arizona-cardinals', 'stl/st-louis-rams', 'sf/san-francisco-49ers', 'sea/seattle-seahawks', 'chi/chicago-bears', 'det/detroit-lions', 'gb/green-bay-packers', 'min/minnesota-vikings', 'atl/atlanta-falcons', 'car/carolina-panthers', 'no/new-orleans-saints', 'tb/tampa-bay-buccaneers'] 
  for t in teams:
    team = t[:3]
    if t[2] == '/':
      team = t[:2] 
    gamelog_url = "http://espn.go.com/nfl/team/depth/_/name/%s" % (team)
    gamelog_res = requests.get(gamelog_url)
    soup = BeautifulSoup(gamelog_res.content)
    table = soup.find('table', class_="tablehead")
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
  
if __name__ == '__main__':
  main()