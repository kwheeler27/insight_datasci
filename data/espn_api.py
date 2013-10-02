import requests
import json
from bs4 import BeautifulSoup
import re
from helpers import *

"""
This script uses ESPN's API to extract info on all players in the NFL.
"""
def main():
  api_key = '7wyyp5rvmfc5wynqy4akxe42'
  req_format = 'http://api.espn.com/v1/sports/football/nfl/athletes?apikey='
  params = '&limit=3'
  url = req_format + api_key + params
  r = requests.get(url)
  dict = json.loads(r.text)
  players = {}
  athlete_list = dict[u'sports'][0][u'leagues'][0][u'athletes']
  for athlete in athlete_list:
    first_name = athlete[u'firstName'].encode('ascii', 'ignore')
    last_name = athlete[u'lastName'].encode('ascii', 'ignore')
    full_name = athlete[u'fullName'].encode('ascii', 'ignore')
    plyr_id = athlete[u'id']
    href = athlete[u'links'][u'web'][u'athletes'][u'href'].encode('ascii', 'ignore')
    players[plyr_id] = [full_name, first_name, last_name, href]
  
  #extracts the player name for gamelog requests
  for k, v in players.items():
    href_str = v[3]
    display_name = re.search(r'/([\w-]+-[\w]+)\?', href_str)
    v.append(display_name.group(1))
      
  #gets game_ids for each player
  id = players.keys()[0]
  name = players[id][4]
  year = 2012
  gamelog_url = "http://espn.go.com/nfl/player/gamelog/_/id/%d/year/%d/%s" % (id, year, name)
  gamelog_res = requests.get(gamelog_url)
  soup = BeautifulSoup(gamelog_res.content)

if __name__ == '__main__':
  main()